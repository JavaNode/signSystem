from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..models.group import Group
from ..models.participant import Participant
import random

class GroupService:
    """分组服务类"""
    
    @staticmethod
    def create_group(db: Session, name: str, description: str = None) -> Group:
        """
        创建分组
        
        Args:
            db: 数据库会话
            name: 组名
            description: 组描述
        
        Returns:
            创建的分组对象
        """
        group = Group(
            name=name,
            description=description
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        return group
    
    @staticmethod
    def get_group_by_id(db: Session, group_id: int) -> Optional[Group]:
        """根据ID获取分组"""
        return db.query(Group).filter(Group.id == group_id).first()
    
    @staticmethod
    def get_all_groups(db: Session) -> List[Group]:
        """获取所有分组"""
        return db.query(Group).all()
    
    @staticmethod
    def update_group(db: Session, group_id: int, 
                    update_data: Dict[str, Any]) -> Optional[Group]:
        """更新分组信息"""
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return None
        
        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)
        
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def delete_group(db: Session, group_id: int) -> bool:
        """删除分组"""
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return False
        
        # 将该组的参赛者移到未分组状态
        db.query(Participant).filter(Participant.group_id == group_id).update(
            {"group_id": None}
        )
        
        db.delete(group)
        db.commit()
        return True
    
    @staticmethod
    def assign_participant_to_group(db: Session, participant_id: int, 
                                   group_id: int) -> bool:
        """将参赛者分配到指定组"""
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        group = db.query(Group).filter(Group.id == group_id).first()
        
        if not participant or not group:
            return False
        
        participant.group_id = group_id
        db.commit()
        return True
    
    @staticmethod
    def remove_participant_from_group(db: Session, participant_id: int) -> bool:
        """将参赛者从组中移除"""
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return False
        
        participant.group_id = None
        db.commit()
        return True
    
    @staticmethod
    def get_group_members(db: Session, group_id: int) -> List[Participant]:
        """获取组内成员"""
        return db.query(Participant).filter(Participant.group_id == group_id).all()
    
    @staticmethod
    def get_ungrouped_participants(db: Session) -> List[Participant]:
        """获取未分组的参赛者"""
        return db.query(Participant).filter(Participant.group_id.is_(None)).all()
    
    @staticmethod
    def auto_group_by_organization(db: Session, max_group_size: int = 20) -> List[Group]:
        """
        按单位自动分组
        
        Args:
            db: 数据库会话
            max_group_size: 每组最大人数
        
        Returns:
            创建的分组列表
        """
        # 获取所有未分组的参赛者
        ungrouped = GroupService.get_ungrouped_participants(db)
        
        # 按单位分类
        org_participants = {}
        for participant in ungrouped:
            org = participant.organization
            if org not in org_participants:
                org_participants[org] = []
            org_participants[org].append(participant)
        
        created_groups = []
        group_counter = 1
        
        # 为每个单位创建分组
        for org, participants in org_participants.items():
            participant_count = len(participants)
            
            if participant_count <= max_group_size:
                # 单位人数不超过最大组数，创建一个组
                group = GroupService.create_group(
                    db, 
                    name=f"第{group_counter}组",
                    description=f"{org} ({participant_count}人)"
                )
                
                # 将该单位所有人分配到这个组
                for participant in participants:
                    participant.group_id = group.id
                
                created_groups.append(group)
                group_counter += 1
            
            else:
                # 单位人数超过最大组数，需要拆分成多个组
                groups_needed = (participant_count + max_group_size - 1) // max_group_size
                
                for i in range(groups_needed):
                    start_idx = i * max_group_size
                    end_idx = min((i + 1) * max_group_size, participant_count)
                    group_participants = participants[start_idx:end_idx]
                    
                    group = GroupService.create_group(
                        db,
                        name=f"第{group_counter}组",
                        description=f"{org} 第{i+1}组 ({len(group_participants)}人)"
                    )
                    
                    # 分配参赛者到组
                    for participant in group_participants:
                        participant.group_id = group.id
                    
                    created_groups.append(group)
                    group_counter += 1
        
        db.commit()
        return created_groups
    
    @staticmethod
    def merge_small_organizations(db: Session, min_group_size: int = 8, 
                                 max_group_size: int = 20) -> List[Group]:
        """
        合并小单位到同一组
        
        Args:
            db: 数据库会话
            min_group_size: 最小组大小
            max_group_size: 最大组大小
        
        Returns:
            创建的分组列表
        """
        # 获取所有未分组的参赛者
        ungrouped = GroupService.get_ungrouped_participants(db)
        
        # 按单位分类
        org_participants = {}
        for participant in ungrouped:
            org = participant.organization
            if org not in org_participants:
                org_participants[org] = []
            org_participants[org].append(participant)
        
        # 分离大单位和小单位
        large_orgs = {}
        small_orgs = {}
        
        for org, participants in org_participants.items():
            if len(participants) >= min_group_size:
                large_orgs[org] = participants
            else:
                small_orgs[org] = participants
        
        created_groups = []
        group_counter = 1
        
        # 处理大单位（每个单位独立成组）
        for org, participants in large_orgs.items():
            if len(participants) <= max_group_size:
                # 创建一个组
                group = GroupService.create_group(
                    db,
                    name=f"第{group_counter}组",
                    description=f"{org} ({len(participants)}人)"
                )
                
                for participant in participants:
                    participant.group_id = group.id
                
                created_groups.append(group)
                group_counter += 1
            else:
                # 拆分成多个组
                groups_needed = (len(participants) + max_group_size - 1) // max_group_size
                
                for i in range(groups_needed):
                    start_idx = i * max_group_size
                    end_idx = min((i + 1) * max_group_size, len(participants))
                    group_participants = participants[start_idx:end_idx]
                    
                    group = GroupService.create_group(
                        db,
                        name=f"第{group_counter}组",
                        description=f"{org} 第{i+1}组 ({len(group_participants)}人)"
                    )
                    
                    for participant in group_participants:
                        participant.group_id = group.id
                    
                    created_groups.append(group)
                    group_counter += 1
        
        # 处理小单位（合并到同一组）
        if small_orgs:
            current_group_participants = []
            current_group_orgs = []
            
            for org, participants in small_orgs.items():
                if len(current_group_participants) + len(participants) <= max_group_size:
                    # 可以加入当前组
                    current_group_participants.extend(participants)
                    current_group_orgs.append(f"{org}({len(participants)}人)")
                else:
                    # 当前组已满，创建新组
                    if current_group_participants:
                        group = GroupService.create_group(
                            db,
                            name=f"第{group_counter}组",
                            description=" + ".join(current_group_orgs)
                        )
                        
                        for participant in current_group_participants:
                            participant.group_id = group.id
                        
                        created_groups.append(group)
                        group_counter += 1
                    
                    # 开始新组
                    current_group_participants = participants[:]
                    current_group_orgs = [f"{org}({len(participants)}人)"]
            
            # 处理最后一组
            if current_group_participants:
                group = GroupService.create_group(
                    db,
                    name=f"第{group_counter}组",
                    description=" + ".join(current_group_orgs)
                )
                
                for participant in current_group_participants:
                    participant.group_id = group.id
                
                created_groups.append(group)
        
        db.commit()
        return created_groups
    
    @staticmethod
    def draw_lots_for_groups(db: Session) -> Dict[str, Any]:
        """为所有组抽签确定出场顺序"""
        groups = GroupService.get_all_groups(db)
        
        if not groups:
            return {"success": False, "message": "没有找到分组"}
        
        # 生成随机顺序
        group_ids = [group.id for group in groups]
        random.shuffle(group_ids)
        
        # 更新抽签顺序
        for order, group_id in enumerate(group_ids, 1):
            group = db.query(Group).filter(Group.id == group_id).first()
            if group:
                group.draw_order = order
        
        db.commit()
        
        # 返回抽签结果
        updated_groups = db.query(Group).order_by(Group.draw_order).all()
        
        return {
            "success": True,
            "message": "抽签完成",
            "results": [
                {
                    "group_id": group.id,
                    "group_name": group.name,
                    "draw_order": group.draw_order,
                    "member_count": group.member_count
                }
                for group in updated_groups
            ]
        }
    
    @staticmethod
    def get_groups_statistics(db: Session) -> Dict[str, Any]:
        """获取分组统计信息"""
        groups = GroupService.get_all_groups(db)
        ungrouped_count = len(GroupService.get_ungrouped_participants(db))
        
        group_stats = []
        total_participants = 0
        total_checked_in = 0
        
        for group in groups:
            group_dict = group.to_dict()
            group_stats.append(group_dict)
            total_participants += group.member_count
            total_checked_in += group.checkin_count
        
        return {
            "total_groups": len(groups),
            "total_participants": total_participants,
            "ungrouped_participants": ungrouped_count,
            "total_checked_in": total_checked_in,
            "overall_checkin_rate": round(total_checked_in / total_participants * 100, 2) if total_participants > 0 else 0,
            "groups": group_stats
        }
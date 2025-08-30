import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image, ImageDraw, ImageFont
import io
import os
from typing import Optional

def generate_qr_code(data: str, size: int = 10, border: int = 4) -> Image.Image:
    """
    生成二维码图片
    
    Args:
        data: 二维码数据
        size: 二维码大小
        border: 边框大小
    
    Returns:
        PIL Image对象
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # 创建带样式的二维码
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer()
    )
    
    return img

def generate_participant_qr(participant_id: int, qr_code_id: str, 
                          participant_name: str = "", 
                          save_path: Optional[str] = None) -> str:
    """
    为参赛者生成专属二维码
    
    Args:
        participant_id: 参赛者ID
        qr_code_id: 二维码标识
        participant_name: 参赛者姓名
        save_path: 保存路径
    
    Returns:
        二维码文件路径
    """
    # 二维码数据格式：checkin:qr_code_id:participant_id
    qr_data = f"checkin:{qr_code_id}:{participant_id}"
    
    # 生成基础二维码
    qr_img = generate_qr_code(qr_data, size=8, border=2)
    
    # 创建带标题的图片
    img_width = qr_img.width
    img_height = qr_img.height + 80  # 为标题预留空间
    
    # 创建新图片
    final_img = Image.new('RGB', (img_width, img_height), 'white')
    
    # 粘贴二维码
    final_img.paste(qr_img, (0, 60))
    
    # 添加标题文字
    draw = ImageDraw.Draw(final_img)
    
    try:
        # 尝试使用系统字体
        font_title = ImageFont.truetype("arial.ttf", 16)
        font_subtitle = ImageFont.truetype("arial.ttf", 12)
    except:
        # 如果没有找到字体，使用默认字体
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # 绘制标题
    title_text = "签到二维码"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (img_width - title_width) // 2
    draw.text((title_x, 10), title_text, fill='black', font=font_title)
    
    # 绘制参赛者姓名
    if participant_name:
        name_bbox = draw.textbbox((0, 0), participant_name, font=font_subtitle)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (img_width - name_width) // 2
        draw.text((name_x, 35), participant_name, fill='black', font=font_subtitle)
    
    # 保存文件
    if save_path is None:
        save_path = f"data/qrcodes/participant_{participant_id}_{qr_code_id}.png"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 保存图片
    final_img.save(save_path, 'PNG', quality=95)
    
    return save_path

def generate_batch_qr_codes(participants: list, output_dir: str = "data/qrcodes") -> list:
    """
    批量生成参赛者二维码
    
    Args:
        participants: 参赛者列表
        output_dir: 输出目录
    
    Returns:
        生成的文件路径列表
    """
    os.makedirs(output_dir, exist_ok=True)
    file_paths = []
    
    for participant in participants:
        save_path = os.path.join(
            output_dir, 
            f"participant_{participant.id}_{participant.qr_code_id}.png"
        )
        
        file_path = generate_participant_qr(
            participant_id=participant.id,
            qr_code_id=participant.qr_code_id,
            participant_name=participant.name,
            save_path=save_path
        )
        
        file_paths.append(file_path)
    
    return file_paths

def create_qr_code_sheet(participants: list, output_path: str = "data/exports/qr_codes_sheet.png") -> str:
    """
    创建二维码打印表格
    
    Args:
        participants: 参赛者列表
        output_path: 输出文件路径
    
    Returns:
        生成的文件路径
    """
    # 每行显示的二维码数量
    codes_per_row = 4
    qr_size = 200
    margin = 20
    text_height = 40
    
    # 计算总行数
    total_rows = (len(participants) + codes_per_row - 1) // codes_per_row
    
    # 计算图片尺寸
    sheet_width = codes_per_row * (qr_size + margin) + margin
    sheet_height = total_rows * (qr_size + text_height + margin) + margin
    
    # 创建画布
    sheet_img = Image.new('RGB', (sheet_width, sheet_height), 'white')
    
    # 生成每个二维码并放置到画布上
    for i, participant in enumerate(participants):
        row = i // codes_per_row
        col = i % codes_per_row
        
        # 生成二维码
        qr_data = f"checkin:{participant.qr_code_id}:{participant.id}"
        qr_img = generate_qr_code(qr_data, size=6, border=1)
        qr_img = qr_img.resize((qr_size, qr_size))
        
        # 计算位置
        x = col * (qr_size + margin) + margin
        y = row * (qr_size + text_height + margin) + margin
        
        # 粘贴二维码
        sheet_img.paste(qr_img, (x, y))
        
        # 添加文字
        draw = ImageDraw.Draw(sheet_img)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        text = f"{participant.name}\n{participant.organization}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x + (qr_size - text_width) // 2
        text_y = y + qr_size + 5
        
        draw.text((text_x, text_y), text, fill='black', font=font)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存文件
    sheet_img.save(output_path, 'PNG', quality=95)
    
    return output_path
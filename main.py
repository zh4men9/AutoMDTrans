# coding: utf-8

from PIL import Image # pip install pillow, 用Image模块操作图片文件
from io import BytesIO # BytesIO是操作二进制数据的模块
import win32clipboard # 用于剪切板 # pip install pywin32, win32clipboard是操作剪贴板的模块
import argparse # 用于传参
import tkinter # 用于msbox
import tkinter.messagebox as msb # 用于msbox
import os # 执行copy命令
import re # 正则化搜索
from pykeyboard import PyKeyboard # 执行快捷键
import pyperclip  # 用于读取剪切板内容
import time

def upload_image_via_picgo():
    k = PyKeyboard()
    k.press_keys([k.control_key, k.shift_key, 'p'])

def send_msg_to_clip(type_data, msg):
    """
    操作剪贴板分四步：
    1. 打开剪贴板：OpenClipboard()
    2. 清空剪贴板，新的数据才好写进去：EmptyClipboard()
    3. 往剪贴板写入数据：SetClipboardData()
    4. 关闭剪贴板：CloseClipboard()

    :param type_data: 数据的格式，
    unicode字符通常是传 win32con.CF_UNICODETEXT
    :param msg: 要写入剪贴板的数据
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(type_data, msg)
    win32clipboard.CloseClipboard()
    
def paste_img(file_img):
    """
    图片转换成二进制字符串，然后以位图的格式写入剪贴板

    主要思路是用Image模块打开图片，
    用BytesIO存储图片转换之后的二进制字符串

    :param file_img: 图片的路径
    """
    # 把图片写入image变量中
    # 用open函数处理后，图像对象的模式都是 RGB
    image = Image.open(file_img)

    # 声明output字节对象
    output = BytesIO()

    # 用BMP (Bitmap) 格式存储
    # 这里是位图，然后用output字节对象来存储
    image.save(output, 'BMP')

    # BMP图片有14字节的header，需要额外去除
    data = output.getvalue()[14:]

    # 关闭
    output.close()

    # DIB: 设备无关位图(device-independent bitmap)，名如其意
    # BMP的图片有时也会以.DIB和.RLE作扩展名
    # 设置好剪贴板的数据格式，再传入对应格式的数据，才能正确向剪贴板写入数据
    send_msg_to_clip(win32clipboard.CF_DIB, data)

def get_args(): #获取相关参数
  parse = argparse.ArgumentParser()
  parse.add_argument('--file_path',type=str,default='None',help='markdown文档位置')
  
  args = parse.parse_args()
  
  return args

def check(args):
  args.file_path = args.file_path.strip()
  print(f"path:{args.file_path}")
  if (args.file_path=='None'): # 检查是否输入文档
    msb.showerror('Error', '请输入文件路径')
    return
  
  elif (args.file_path.split('.')[-1] != "MD" \
    and args.file_path.split('.')[-1] != 'md'): # 检查是否是markdown文档
    msb.showerror('Error', '请选择markdown文件')
    return
  
  elif (not os.path.exists(args.file_path)): # 检查文档是否存在
    msb.showerror('Error', '未找到文件，请重新输入文件路径')
    return
  
def strip_path(pic_path): # 剥离出图片的路径
  # 三种形式，![]()、![[]]、<img src=>
  if (pic_path[0]=='<' and pic_path[-1]=='>'):# <img src=>
    pass # todo
  elif (pic_path[0]=='!' and pic_path[-1]==']'): # ![[]]
    pic_path = pic_path[3:-2]
    print(pic_path)
  elif (pic_path[0]=='!' and pic_path[-1]==')'): # ![]()
    pic_path = pic_path[4:-1]
    print(pic_path)
    
  return pic_path

def put_image_to_clip(image): # 将图片放入剪切板
    img_byte_arr = io.BytesIO() 
    pb = pasteboard.Pasteboard()

    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    pb.set_contents(img_byte_arr, pasteboard.PNG)

def upload(args, pic_path_total): # 遍历每一张图片，上传到图床，替换掉原来文档内容
  
  # 文档目录
  if ('\\' in args.file_path):
    pos = args.file_path.rfind('\\')
    file_dir = args.file_path[:pos+1]
    print(f'file_dir:{file_dir}')
  elif ('/' in args.file_path):
    pos = args.file_path.rfind('/')
    file_dir = args.file_path[:pos+1]
    print(f'file_dir:{file_dir}')
  
  # 遍历每张图片上传
  new_file_path = args.file_path + '.tmp'
  with open(new_file_path,'r',encoding='utf-8') as mdfile:
    data = mdfile.read()
    
    for pic_path in pic_path_total:
      pure_pic_path = file_dir + strip_path(pic_path.strip())
      print(f'pic_path:{pure_pic_path}')
      if (os.path.exists(pure_pic_path) == True):    
        # 将图片放入剪切板内存
        paste_img(pure_pic_path)
        
        # 激活PicGo快捷键让其上传剪切板图片
        upload_image_via_picgo()
        
        # 监听是否收到剪切板改变，并判断是否是图床的链接
        recent_value = pyperclip.paste() 			# 读取剪切板复制的内容
        while True:
          tmp_value = pyperclip.paste() 			# 读取剪切板复制的内容

          try:
              if tmp_value != recent_value:				 #如果检测到剪切板内容有改动，那么就进入文本的修改
                  recent_value = tmp_value
                  print(recent_value)
                  # 读取剪切板链接，替换掉原文档对应内容
                  time.sleep(0.1)
                  data = data.replace(pic_path, recent_value)
                  break
          except KeyboardInterrupt:  # 如果有ctrl+c，那么就退出这个程序。  （不过好像并没有用。无伤大雅）
              break
  print(data)
  mdfile.close()
  msb.showinfo('Success!', '转换成功！')

def trans(args):
  
  # 备份文档
  cmd = 'copy "' + args.file_path + '" "' + args.file_path + '.tmp"'
  os.system(cmd)
  
  new_file_path = args.file_path + '.tmp'
  
  # 文件所在目录
  dir_path_list = args.file_path
  
  # 寻找文档中图片链接，使用正则表达式搜索
  pic_path_total = []
  with open(new_file_path,'r',encoding='utf-8') as mdfile:
    data = mdfile.read()
    print(data)
  mdfile.close()
  
  re_pattern = ['!\[.*\]\(.*\)','!\[\[.*\]\]','<.* src=[\'\"].*[\'\"] .*>'] # ![]()形式，![[]]形式，<img src=''>形式
  
  for parttern in re_pattern:
    # print(parttern)
    pic_path = re.findall(parttern, data)
    # print(pic_path)
    if (0 != len(pic_path)):
      pic_path_total = pic_path_total + pic_path
  print(f'pic_path_total:{pic_path_total}')
  
  upload(args, pic_path_total)
  
def main():
  args = get_args()
  check(args)
  trans(args)
  
if __name__ == '__main__':
  main()  
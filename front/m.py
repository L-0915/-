# 安装依赖：pip install qrcode[pil]
import qrcode

# 生成二维码
img = qrcode.make('http://10.103.9.39:5173')
img.save('travel_app_qr.png')

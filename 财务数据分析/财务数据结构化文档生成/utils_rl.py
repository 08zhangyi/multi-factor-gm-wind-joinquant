import  reportlab
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors, fonts
import matplotlib.pyplot as plt
import time
import os


# 生成文本段落
def rl_text(string):
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))  # 注册字体
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(fontName='SimSun', name='Song', leading=20, fontSize=12))  # 自己增加新注册的字体
    p = Paragraph(string, styles['Song'])  # 使用新字体
    return p


# 生成表格段落
def rl_table(data_list):
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))  # 注册字体
    fonts.addMapping('SimSun', 0, 0, 'SimSun')
    fonts.addMapping('SimSun', 0, 1, 'SimSun')
    component_table = Table(data_list)

    style_list = [('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                  ('GRID', (0, 0), (-1, -1), 0.2, colors.black),
                  ('FONTSIZE', (0, 0), (-1, -1), 10), ('FONT', (0, 0), (-1, -1), 'SimSun')]
    mytable_style = TableStyle(style_list)
    component_table.setStyle(mytable_style)
    return component_table


# 生成图片段落
def rl_photo(file_path, height, width):
    img = Image(file_path)
    img.drawHeight = height*cm
    img.drawWidth = width*cm
    return img


# 画饼图辅助函数
def rl_pie_chart(title, datas, texts, file_name=''):
    # title为标题
    # datas=[12.3, 4.5, 6.7, 9.8]
    # texts=['卢神1', '卢神12', ''卢神13', ''卢神14']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 内部函数
    def func(pct, allvals):
        return "{:.1f}%".format(pct)
    fig, ax = plt.subplots(figsize=(18, 12), subplot_kw=dict(aspect="equal"))
    wedges, _, autotexts = ax.pie(datas, autopct=lambda pct: func(pct, datas), textprops=dict(color="w"))
    ax.legend(wedges, texts, fontsize=20, title_fontsize=20, title="内容说明", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=20, weight="bold")
    ax.set_title(title, size=24)
    plt.savefig('output\\temp'+file_name+'.png')
    time.sleep(0.1)
    img = rl_photo('output\\temp'+file_name+'.png', 12, 18)
    return img


# 多段落整合文档
def rl_build(rl_object_list, file_path='output\\temp.pdf'):
    pdf = SimpleDocTemplate(file_path)
    pdf.multiBuild(rl_object_list)


# 清空文件夹
def clean_path():
    path = 'output'
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)


if __name__ == '__main__':
    p1 = rl_text('一盒的hi受到司法和卢神福未发货')
    p2 = rl_text('\0')
    p3 = rl_text('卢神创新NoID发货时覅')
    component_table = rl_table([['卢神1', '卢神2', '卢神3'], [1.0, 2.3, 4.5], [5.6, 7.8, 9.0]])
    img = rl_pie_chart('卢神', [0.1, 0.2, 0.6], ['卢神', '卢神2', '卢神3'])
    rl_build([p1, p2, p3, component_table, img])
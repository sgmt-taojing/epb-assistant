#!/usr/bin/env python3
"""
环保执法文书 PDF 生成器
基于 reportlab 生成专业 PDF 版执法文书
"""

import os, json
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT = 'Helvetica'
WIDTH, HEIGHT = A4

styles = getSampleStyleSheet()

def styled_para(text, size=11, bold=False, color='#1B4332', align='left', space_after=8):
    return Paragraph(
        f'<font name="{FONT}" size="{size}" color="{color}"><b>{"Y" if bold else ""}</b>{text.replace("<b>","").replace("</b>","")}</font>',
        ParagraphStyle('custom', fontName=FONT, fontSize=size,
                      textColor=colors.HexColor(color),
                      alignment={'left':0,'center':1,'right':2}[align],
                      spaceAfter=space_after)
    )

def para(text, size=11, bold=False, color='#222222', align='left', space_after=6):
    fname = FONT + '-Bold' if bold else FONT
    return Paragraph(
        f'<font name="{fname}" size="{size}" color="{color}">{text}</font>',
        ParagraphStyle('custom', fontName=fname, fontSize=size,
                      textColor=colors.HexColor(color),
                      alignment={'left':0,'center':1,'right':2}[align],
                      spaceAfter=space_after)
    )

def make_table(data, col_widths=None, header_bg='#1B4332', header_fg='#FFFFFF'):
    t = Table(data, colWidths=col_widths or [WIDTH/cm*0.3*k for k in [1]*len(data[0])])
    style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(header_bg)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor(header_fg)),
        ('FONTNAME', (0,0), (-1,0), FONT + '-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F2F8F4')]),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]
    t.setStyle(TableStyle(style))
    return t

def generate_xzcfjds_pdf(party, fact, law, result, fine, case_id=None):
    cid = case_id or f'{date.today().strftime("%Y%m%d")}-001'
    output = os.path.join(os.path.dirname(__file__), '..', 'outputs', f'{cid}.pdf')
    os.makedirs(os.path.dirname(output), exist_ok=True)

    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    story = []
    # 标题
    story.append(para('行 政 处 罚 决 定 书', 20, bold=True, color='#1B4332', align='center', space_after=4))
    story.append(para(f'济环罚字〔{date.today().year}〕第{cid.split("-")[-1]}号', 10, color='#666666', align='center', space_after=16))
    story.append(HRFlowable(width='100%', thickness=2, color='#1B4332'))
    story.append(Spacer(1, 0.4*cm))

    # 基本信息表格
    story.append(make_table([
        ['案    号', cid, '处罚日期', date.today().strftime('%Y-%m-%d')],
        ['当事人', party, '所属行业', '（待填写）'],
        ['案件类型', '（污染类型）', '涉案金额', f'{fine}万元'],
    ], col_widths=[3*cm, 6*cm, 3*cm, 5.5*cm], header_bg='#D8E8DC', header_fg='#1B4332'))
    story.append(Spacer(1, 0.4*cm))

    # 违法事实
    story.append(para('一、违法事实', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(fact, 11, space_after=10))

    # 证据
    story.append(para('二、证据材料', 12, bold=True, color='#1B4332', space_after=4))
    evidences = [
        ['序号', '证据类型', '证据名称/编号', '证明内容'],
        ['1', '现场笔录', '现场检查（勘察）笔录', '证明现场检查过程及发现的违法行为'],
        ['2', '书    证', '环评批复/排污许可证', '证明当事人主体资格及环保手续情况'],
        ['3', '监测报告', '（检测机构+报告编号）', '证明污染物超标/违法排放事实'],
        ['4', '影像资料', '现场照片/视频', '证明违法行为客观存在'],
        ['5', '询问笔录', '被询问人签名笔录', '证明当事人对违法事实的陈述确认'],
    ]
    story.append(make_table(evidences, col_widths=[1.5*cm, 3*cm, 5*cm, 7.5*cm]))
    story.append(Spacer(1, 0.4*cm))

    # 违反法律
    story.append(para('三、违反法律', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(f'上述行为违反了 {law} 的相关规定。', 11, space_after=10))

    # 处罚依据
    story.append(para('四、处罚依据', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(f'依据 {law} 的规定，对当事人作出如下行政处罚：', 11, space_after=8))

    # 处罚内容
    story.append(make_table([
        ['处罚项目', '内容'],
        ['罚款金额', f'人民币（大写）{"壹" if fine=="1" else "壹拾" if fine=="10" else fine}万{"零" if fine=="1" else "零"}仟元整（¥{float(fine)*10000:.0f}元）'],
        ['缴纳期限', '自收到本决定书之日起15日内'],
        ['缴纳方式', '凭本决定书到济南市生态环境局财务室开具缴款通知书'],
        ['逾期后果', '每日按罚款数额的3%加处罚款；不履行的申请法院强制执行'],
    ], col_widths=[3*cm, 14*cm]))
    story.append(Spacer(1, 0.4*cm))

    # 救济途径
    story.append(para('五、复议与诉讼', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para('当事人如不服本处罚决定，可在收到本决定书之日起60日内向济南市人民政府申请行政复议，或在6个月内向有管辖权的人民法院提起行政诉讼。', 11, space_after=8))
    story.append(para('逾期不申请行政复议、不提起行政诉讼，又不履行本处罚决定的，本机关将依法申请人民法院强制执行。', 11, space_after=16))

    # 署名
    story.append(Spacer(1, 0.5*cm))
    story.append(para('济南市生态环境局（印章）', 11, align='right', space_after=4))
    story.append(Spacer(1, 0.3*cm))
    story.append(para(date.today().strftime('%Y年%m月%d日'), 11, align='right'))

    doc.build(story)
    return output, cid

def generate_zlgztz_pdf(party, fact, requirement, deadline, case_id=None):
    cid = case_id or f'{date.today().strftime("%Y%m%d")}-002'
    output = os.path.join(os.path.dirname(__file__), '..', 'outputs', f'{cid}.pdf')
    os.makedirs(os.path.dirname(output), exist_ok=True)

    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story.append(para('责令改正违法行为决定书', 20, bold=True, color='#1B4332', align='center', space_after=4))
    story.append(para(f'济环责改字〔{date.today().year}〕第{cid.split("-")[-1]}号', 10, color='#666666', align='center', space_after=12))
    story.append(HRFlowable(width='100%', thickness=2, color='#1B4332'))
    story.append(Spacer(1, 0.4*cm))
    story.append(make_table([['当事人', party], ['案号', cid], ['出具日期', date.today().strftime('%Y-%m-%d')]],
                            col_widths=[3*cm, 14.5*cm], header_bg='#D8E8DC', header_fg='#1B4332'))
    story.append(Spacer(1, 0.4*cm))
    story.append(para('一、违法事实', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(fact, 11, space_after=10))
    story.append(para('二、责令改正内容', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(requirement, 11, space_after=10))
    story.append(para('三、改正期限', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(f'限于 {deadline} 前完成整改。', 11, space_after=6))
    story.append(para('如逾期未改正，我局将依法启动按日连续处罚程序（每日按罚款数额的3%加处罚款）或采取进一步的行政强制措施。', 11, space_after=10))
    story.append(para('四、后续要求', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para('整改完成后，当事人应向我局提交书面整改报告（含整改前后对比照片及相关证明材料）。我局将在收到报告后10个工作日内依法进行核查。', 11, space_after=16))
    story.append(Spacer(1, 0.5*cm))
    story.append(para('济南市生态环境局（印章）', 11, align='right', space_after=4))
    story.append(para(date.today().strftime('%Y年%m月%d日'), 11, align='right'))
    doc.build(story)
    return output, cid

def generate_xcjcbcjl_pdf(party, location, inspector, date_str, facts, law, case_id=None):
    cid = case_id or f'XCJC-{date.today().strftime("%Y%m%d")}'
    output = os.path.join(os.path.dirname(__file__), '..', 'outputs', f'{cid}.pdf')
    os.makedirs(os.path.dirname(output), exist_ok=True)
    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story.append(para('现 场 检 查（勘 察）笔 录', 20, bold=True, color='#1B4332', align='center', space_after=8))
    story.append(HRFlowable(width='100%', thickness=2, color='#1B4332'))
    story.append(Spacer(1, 0.3*cm))
    story.append(make_table([
        ['当事人', party],
        ['检查时间', date_str],
        ['检查地点', location],
        ['执法人员', inspector],
        ['记 录 人', '（签名）'],
        ['天气状况', '（填写当日天气）'],
    ], col_widths=[3.5*cm, 14*cm], header_bg='#D8E8DC', header_fg='#1B4332'))
    story.append(Spacer(1, 0.4*cm))
    story.append(para('一、检查情况', 12, bold=True, color='#1B4332', space_after=4))
    story.append(para(facts, 11, space_after=10))
    story.append(para('二、现场取证情况', 12, bold=True, color='#1B4332', space_after=4))
    story.append(make_table([
        ['取证类型', '数量', '存放位置/备注'],
        ['现场照片', '（张）', '（填写）'],
        ['现场录像', '（段）', '（填写）'],
        ['采样记录', '（个）', '（填写检测项目）'],
        ['书证材料', '（份）', '（填写名称）'],
    ], col_widths=[4*cm, 3*cm, 10.5*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(para(f'三、涉嫌违反法律条款\n{law}', 12, bold=True, color='#1B4332', space_after=4))
    story.append(Spacer(1, 0.5*cm))
    story.append(para(f'被检查单位负责人（签名）：_______________    {date.today().strftime("%Y年%m月%d日")}', 10, align='right', space_after=6))
    story.append(para('执法人员（签名）：_______________    _______________', 10, align='right'))
    doc.build(story)
    return output, cid

def generate_pdf(doc_type, case_data, output_path=None):
    generators = {
        'xzcfjds': lambda d: generate_xzcfjds_pdf(d.get('party',''), d.get('fact',''), d.get('law',''), d.get('result',''), d.get('fine','10'), d.get('case_id')),
        'zlgztz': lambda d: generate_zlgztz_pdf(d.get('party',''), d.get('fact',''), d.get('requirement',''), d.get('deadline',''), d.get('case_id')),
        'xcjcbcjl': lambda d: generate_xcjcbcjl_pdf(d.get('party',''), d.get('location',''), d.get('inspector',''), d.get('date',''), d.get('facts',''), d.get('law',''), d.get('case_id')),
    }
    if doc_type not in generators:
        raise ValueError(f'不支持的文书类型: {doc_type}')
    path, cid = generators[doc_type](case_data)
    if output_path:
        import shutil
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copy(path, output_path)
        return output_path, cid
    return path, cid

if __name__ == '__main__':
    import sys
    doc_type = sys.argv[1] if len(sys.argv) > 1 else 'xzcfjds'
    output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    path, cid = generate_pdf(doc_type, data, output_path)
    print(f'OK|{path}|{cid}')

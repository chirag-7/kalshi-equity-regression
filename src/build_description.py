"""Create the editable course description and its Markdown counterpart."""
from pathlib import Path
import json
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports"
doc=Document()
md=[]
section=doc.sections[0]
section.top_margin=section.bottom_margin=Inches(.65)
section.left_margin=section.right_margin=Inches(.7)
section.page_width=Inches(8.5);section.page_height=Inches(11)
for name in ["Normal","Title","Subtitle","Heading 1","Heading 2","List Bullet","Caption"]:
    style=doc.styles[name];style.font.name="Arial";style.font.color.rgb=RGBColor(0,0,0)
doc.styles["Normal"].font.size=Pt(10.5)
doc.styles["Normal"].paragraph_format.space_after=Pt(5)
doc.styles["Normal"].paragraph_format.line_spacing=1.04
doc.styles["Title"].font.size=Pt(20)
doc.styles["Title"].paragraph_format.space_after=Pt(6)
doc.styles["Heading 1"].font.size=Pt(12)
doc.styles["Heading 1"].paragraph_format.space_before=Pt(9)
doc.styles["Heading 1"].paragraph_format.space_after=Pt(5)
doc.styles["List Bullet"].font.size=Pt(10.5)
doc.styles["List Bullet"].paragraph_format.space_after=Pt(4)
doc.styles["Caption"].font.size=Pt(9.5)
doc.styles["Caption"].font.italic=False
doc.styles["Caption"].font.bold=False
doc.styles["Caption"].paragraph_format.space_after=Pt(7)
footer=section.footer.paragraphs[0]
footer.alignment=2
footer.add_run("STAT GU4205 GR5205  |  ").font.size=Pt(8)
field=OxmlElement("w:fldSimple");field.set(qn("w:instr"),"PAGE");footer._p.append(field)
ins=json.loads((OUT/"tables/insights.json").read_text())
sample=json.loads((ROOT/"data/metadata/sample_summary.json").read_text())
stats=pd.read_csv(OUT/"tables/descriptive_statistics.csv",index_col="variable")


def title(text):
    doc.add_paragraph(text,"Title");md.extend(["# "+text,""])


def heading(text):
    doc.add_heading(text,level=1);md.extend(["## "+text,""])


def para(text,style=None):
    p=doc.add_paragraph(text,style=style)
    md.extend([("- " if style=="List Bullet" else "")+text,""])
    return p


def page():doc.add_page_break()


def table(headers, rows, widths):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,h in zip(t.rows[0].cells,headers):c.text=h
    for row in rows:
        for c,v in zip(t.add_row().cells,row):c.text=str(v)
    for rowno,row in enumerate(t.rows):
        for i,cell in enumerate(row.cells):
            cell.width=Inches(widths[i]);cell.vertical_alignment=1
            tcpr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement("w:tcBorders")
            for edge in ["top","left","bottom","right"]:
                b=OxmlElement("w:"+edge);b.set(qn("w:val"),"single");b.set(qn("w:sz"),"4");b.set(qn("w:color"),"D9D9D9");borders.append(b)
            tcpr.append(borders)
            margins=OxmlElement("w:tcMar")
            for edge in ["top","bottom","left","right"]:
                n=OxmlElement("w:"+edge);n.set(qn("w:w"),"70");n.set(qn("w:type"),"dxa");margins.append(n)
            tcpr.append(margins)
            if rowno==0:
                sh=OxmlElement("w:shd");sh.set(qn("w:fill"),"E8EEF1");tcpr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(0)
                p.paragraph_format.line_spacing=1.0
                if i>0:p.alignment=1
                for r in p.runs:r.font.size=Pt(9.5);r.bold=rowno==0
        cant=OxmlElement("w:cantSplit");row._tr.get_or_add_trPr().append(cant)
    repeat=OxmlElement("w:tblHeader");t.rows[0]._tr.get_or_add_trPr().append(repeat)
    md.append("| "+" | ".join(headers)+" |")
    md.append("| "+" | ".join(["---"]*len(headers))+" |")
    md.extend(["| "+" | ".join(map(str,r))+" |" for r in rows]);md.append("")
    doc.add_paragraph().paragraph_format.space_after=Pt(0)


def figure(name, caption):
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(3);p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(OUT/"figures"/(name+".png")),width=Inches(7.0))
    p=doc.add_paragraph(caption,"Caption")
    md.extend([f"![{name.replace('_',' ')}](figures/{name}.png)","",caption,""])


def mathrun(text):
    r=OxmlElement("m:r");t=OxmlElement("m:t");t.text=text;r.append(t);return r


def sub(base,index):
    n=OxmlElement("m:sSub");e=OxmlElement("m:e");e.append(mathrun(base));s=OxmlElement("m:sub");s.append(mathrun(index));n.extend([e,s]);return n


def equation(number, additions):
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(7)
    om=OxmlElement("m:oMath")
    chunks=[f"{number}.  ",( "Y","t")," = α + ",("β","M"),("M","t")," + ",("β","T"),("T","t")," + ",("β","V"),("V","t")]+additions+[" + ",("ε","t")]
    for c in chunks:om.append(sub(*c) if isinstance(c,tuple) else mathrun(c))
    p._p.append(om)
    for r in om.iter(qn("m:r")):
        rp=OxmlElement("w:rPr");sz=OxmlElement("w:sz");sz.set(qn("w:val"),"21");rp.append(sz);r.insert(0,rp)
    base=r"Y_t=\alpha+\beta_M M_t+\beta_T T_t+\beta_V V_t"
    extra=["",r"+\eta C_t",r"+\eta C_t+\delta D_t",r"+\eta C_t+\delta D_t+\lambda C_tD_t"][number-1]
    md.extend([f"**Model {number}**", "", "$$"+base+extra+r"+\varepsilon_t$$",""])


def link(label,url):
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(3)
    h=OxmlElement("w:hyperlink");h.set(qn("r:id"),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement("w:r");pr=OxmlElement("w:rPr");sz=OxmlElement("w:sz");sz.set(qn("w:val"),"18");pr.append(sz);r.append(pr)
    t=OxmlElement("w:t");t.text=label;r.append(t);h.append(r);p._p.append(h)
    md.extend([f"[{label}]({url})",""])


title("Kalshi Rate Expectations and Small Cap Relative Returns")
para("STAT GU4205 GR5205  |  Required project description  |  20 November 2026")
heading("Research question")
para("Do changes in Kalshi's expected Fed rate help explain small-cap returns relative to large-cap returns, beyond market returns, Treasury yields and VIX? Does this relationship differ on CPI release days?")
para("We will study IWM, which tracks the Russell 2000, relative to SPY, which tracks the S&P 500. Prior research connects financing constraints with stronger responses to monetary policy. This motivates a size comparison, but our study will not directly test borrowing costs. We are studying same-day associations, rather than claiming that Kalshi causes stock returns or predicts tomorrow's return.")
heading("Team members")
team=json.loads((ROOT/"config/team.json").read_text())
table(["Name","UNI"],[[m["name"],m["uni"]] for m in team],[4.7,2.3])
para("Complete the team list before submission. Four places are shown; the assignment allows three to five members.")
heading("Data collected")
para("Our daily data collection contains 7,657 Kalshi date-and-meeting observations from July 2021 to October 2026. These are expected rates derived by Diercks, Katz and Wright from contracts on different possible Fed outcomes. Other sources are Yahoo Finance for adjusted IWM and SPY prices, Kenneth French for equity factors, FRED for yields and VIX, and BLS and the Federal Reserve for announcement dates.")
para("The preliminary overlap runs from 2 December 2021 to 30 September 2026: 1,143 candidate trading days, 40 Fed meeting targets and 54 CPI days. We compare the same upcoming meeting at both endpoints, exclude Fed decision days, and drop dates missing a required input. The sample ends in September because that is the endpoint of our collected equity-factor file.")
para("We also downloaded minute and hourly candles directly from Kalshi for a June 2023 Fed contract. Hourly data will help align expectations with the equity close; minute data provides a closer view around CPI releases. The current daily archive uses UTC days, so its statistics below are preliminary. The synchronized sample for the final regressions has not yet been constructed.")

page()
heading("Variables and descriptive statistics")
para("Y is the daily adjusted IWM return minus the adjusted SPY return. Positive Y means small caps outperformed large caps that day. C is yesterday's expected Fed rate minus today's expected rate, using the same meeting; positive C means expectations moved toward lower rates. One basis point is 0.01 percentage point.")
para("M is the broad market excess return, T is the change in the 2-year Treasury yield, and V is the change in VIX. D equals 1 on an official CPI release day and 0 otherwise. The interaction is C multiplied by D.")
rows=[]
for key,label in [("relative_return_pp","Y  Relative return in pp"),("kalshi_easing_bps","C  Kalshi revision in bp"),("market_excess_pct","M  Market return in %"),("yield2_change_bps","T  Yield change in bp"),("vix_change_points","V  VIX change in points")]:
    s=stats.loc[key];rows.append([label]+[f"{0 if abs(s[k])<.005 else s[k]:.2f}" for k in ["mean","std","5%","95%"]])
table(["Variable and unit","Mean","SD","5th pct","95th pct"],rows,[3.1,1,1,1,1])
para("All five rows use the same 1,143 candidate dates. SD is the standard deviation; pp means percentage points and bp means basis points. The 5th and 95th percentiles show the middle 90% of the observations.")
para(f"Small caps underperformed by {abs(ins['relative_return_mean_pp']):.2f} percentage point per day on average, while the daily relative-return standard deviation was {ins['relative_return_sd_pp']:.2f}. This is a noisy outcome: most individual days tell us little on their own.")
heading("CPI days and changes in expectations")
table(["Day type","Days","Mean absolute C in bp","Median absolute C in bp"],
      [["Other days","1,089",f"{ins['other_mean_abs_revision_bps']:.2f}",f"{ins['other_median_abs_revision_bps']:.2f}"],
       ["CPI days","54",f"{ins['cpi_mean_abs_revision_bps']:.2f}",f"{ins['cpi_median_abs_revision_bps']:.2f}"]],[2.0,1.0,2.0,2.0])
para(f"The average absolute revision is about {ins['mean_abs_revision_ratio']:.1f} times larger on CPI days. This makes CPI a useful setting for the interaction question, although larger revisions do not by themselves imply a different stock-return slope.")
para(f"About {100*ins['zero_revision_share']:.1f}% of candidate days have no change in the source expectation. Only 1,077 of the 1,143 dates have positive reported target-contract volume at both endpoints. Unchanged expectations can reflect either little news or stale trading, so quote quality needs attention before estimation.")
heading("Why these conventional controls")
para("Market return accounts for unequal market exposure that may remain after subtracting the ETF returns. The 2-year yield gives us a conventional rate-market benchmark. VIX accounts for changes in expected equity volatility. Together they ask whether Kalshi adds information beyond familiar market measures. We will check their correlation rather than assume they are independent.")

page()
heading("Equity performance and CPI repricing")
figure("01_equity_performance",f"Figure 1. Adjusted prices indexed to 100 on 1 December 2021, through 30 September 2026. IWM gained {ins['iwm_total_return_pct']:.1f}% and SPY gained {ins['spy_total_return_pct']:.1f}%. The gap motivates examining relative performance, but cannot be attributed to rate expectations alone. This plot uses all available equity dates in that period, not only the regression candidate dates.")
figure("02_cpi_repricing",f"Figure 2. Absolute Kalshi revisions on CPI and other candidate dates. The median is {ins['cpi_median_abs_revision_bps']:.2f} bp on CPI days and {ins['other_median_abs_revision_bps']:.2f} bp on other days. Points show individual observations; boxes show the middle half. The vertical scale is linear up to 1 bp and logarithmic above it. These are source UTC daily observations; no return-response conclusion is drawn here.")

page()
heading("Trading activity and the minute data")
figure("03_horizon_volume_repricing","Figure 3. Three dimensions in one plot: days until the Fed meeting on the horizontal axis, absolute rate revision on the vertical axis, and daily target-contract volume in colour. The uneven activity and repeated zero changes show why more calendar observations do not always mean more information. Colour uses log10 of one plus volume so both low and high activity remain visible. This is descriptive evidence from the source daily series.")
figure("04_minute_cpi_example",f"Figure 4. Minute trade prices for FED-23JUN-T5.25 on 13 June 2023. The contract paid YES if the upper-bound Fed rate was above 5.25% after the next day's meeting. The plotted prices range from {ins['minute_plot_min_price_cents']:.0f} to {ins['minute_plot_max_price_cents']:.0f} cents. There are {ins['minute_trade_bars_in_plot']} traded minutes shown, with no invented observations between them. The dashed line marks the 08:30 CPI release. A single threshold price is a probability measure, not the expected rate C used in the daily models.")

page()
heading("Four regression models")
para("We will estimate the following models on one common synchronized daily sample. Each model adds one feature to the previous model.")
equation(1,[])
equation(2,[" + η",("C","t")])
equation(3,[" + η",("C","t")," + δ",("D","t")])
equation(4,[" + η",("C","t")," + δ",("D","t")," + λ",("C","t"),("D","t")])
para("Model 1 is the conventional benchmark. Model 2 adds Kalshi. Model 3 allows a different average return on CPI days. Model 4 also allows the Kalshi slope to change: it is η on other days and η + λ on CPI days. Thus λ = 0 tests whether the slopes differ. It does not test whether the stock return itself equals zero.")
heading("Objectives for the analysis")
para("Test whether adding Kalshi improves explanatory fit and whether its coefficient differs from zero, after accounting for the conventional controls.","List Bullet")
para("Test whether CPI days have a different baseline relative return and a different sensitivity to Kalshi revisions. Report coefficient estimates and confidence intervals, including the CPI-day slope η + λ.","List Bullet")
para("Check whether any result survives stricter liquidity filters, influential-date checks and changes in the meeting cycles included.","List Bullet")
heading("Estimation and checks")
para("We will use OLS and allow errors to be related within the same Fed meeting cycle. We will inspect residuals, multicollinearity and influential observations, then compare with Huber robust regression and leave one meeting cycle out at a time. The main models use a small control set. Style factors and the yield-curve slope are secondary checks; SMB closely resembles the relative-size outcome.")
para("Hourly and minute observations will first improve timing and data-quality checks. A separate hourly return regression would also need matched intraday equity prices and controls. We will not treat extra minute bars as extra independent CPI events. No return regressions or significance results are claimed in this preliminary description.")
heading("Selected sources")
link("Kalshi data and construction  Diercks Katz and Wright public research archive","https://github.com/jdkatz21/Prediction_Markets_Public")
link("Kalshi historical minute and hourly candlestick documentation","https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks")
link("Daily equity factors  Kenneth French data library","https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
link("Motivation  Ehrmann and Fratzscher 2004 Taking Stock","https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp354.pdf")
para("Full source links, retrieval records, data definitions and reproducible Python scripts accompany this description in the repository.")

doc.core_properties.title="Kalshi Rate Expectations and Small Cap Relative Returns"
doc.core_properties.subject="STAT GU4205 GR5205 required project description"
doc.core_properties.author=""
for root in [doc.styles.element,doc._element]:
    for border in list(root.iter(qn("w:pBdr"))):border.getparent().remove(border)
doc.save(OUT/"project_description.docx")
(OUT/"project_description.md").write_text("\n".join(md)+"\n")
print(OUT/"project_description.docx")

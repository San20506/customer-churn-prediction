from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

def create_churn_report():
    doc = Document()
    
    # Title Page
    title = doc.add_heading('Project Report: Customer Churn Prediction & Risk Analysis System', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f"Date: {datetime.now().strftime('%d %B, %Y')}")
    doc.add_paragraph("Company: Skipper Pipes")
    doc.add_paragraph("Subject: Data-Driven B2B Retention Strategy and Predictive Analytics")
    
    doc.add_page_break()
    
    # 1. Executive Summary
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph(
        "The Customer Churn Prediction Model is a sophisticated analytical system designed to mitigate revenue loss "
        "by identifying at-risk B2B customers (Plumbers and Retailers) before they cease transactions. "
        "By utilizing a multi-level modeling approach—combining RFM analysis, machine learning (XGBoost), "
        "and Survival Analysis—the system provides actionable insights into customer health, priority-based "
        "retention lists, and geographic risk heatmaps."
    )
    
    # 2. Project Objectives
    doc.add_heading('2. Project Objectives', level=1)
    objectives = [
        "Develop a standardized metric for 'Churn' based on actual purchase behavior (183-day threshold).",
        "Segment customers into actionable groups such as 'Loyal Active', 'At Risk', and 'Churned'.",
        "Implement predictive models to forecast the probability and timing (Time-to-Churn) of future exits.",
        "Analyze geographic (State) and channel (Retailer/Distributor) correlations with churn rates.",
        "Provide sales teams with a high-priority contact list of high-value drifting customers."
    ]
    for obj in objectives:
        doc.add_paragraph(obj, style='List Bullet')
        
    # 3. Technical Architecture (Multi-Level System)
    doc.add_heading('3. Technical Architecture', level=1)
    doc.add_paragraph(
        "The system employs a hierarchical analysis structure to ensure both breadth and depth of insights:"
    )
    
    levels = [
        "Level 1: RFM Analysis (Recency, Frequency, Monetary) - Provides immediate behavioral segmentation and calculates the 'RFM Health Score'.",
        "Level 2: ML Classification (XGBoost & Logistic Regression) - Predicts binary churn probability and identifies key risk drivers (e.g., purchase gap increases).",
        "Level 3: Survival Analysis (Cox Proportional Hazards) - Models the 'lifespan' of a customer and predicts when exactly a churn event is likely to occur.",
        "Drift Detection - A dedicated monitor for inter-purchase gaps, flagging customers whose buying frequency is slowing down compared to their historical norm.",
        "Geographic & Channel Analytics - Cross-references risk data with State, Retailer, and Distributor hierarchies to identify systemic issues."
    ]
    for level in levels:
        doc.add_paragraph(level, style='List Number')
    
    # 4. Key Performance Indicators & Segments
    doc.add_heading('4. KPIs and Customer Segmentation', level=1)
    doc.add_paragraph("The system categorizes all customers based on their 183-day Recency benchmark:")
    
    # Add Table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Segment'
    hdr_cells[1].text = 'Description'
    hdr_cells[2].text = 'Action Priority'
    
    segments = [
        ("At Risk High Value", "Loyal customers showing recent drifting behavior.", "Level 1 (Critical)"),
        ("At Risk", "Active customers with declining frequency.", "Level 2 (High)"),
        ("Churned Out Recently", "Zero activity for 183-365 days.", "Level 3 (Win-back)"),
        ("Loyal Active", "Recent and Frequent buyers.", "Level 5 (Relationship Mgmt)"),
        ("Churned Out Long Term", "Inactive for 360+ days.", "Level 4 (Database Cleanup)")
    ]
    
    for seg, desc, priority in segments:
        row_cells = table.add_row().cells
        row_cells[0].text = seg
        row_cells[1].text = desc
        row_cells[2].text = priority

    # 5. Advanced Feature Insights
    doc.add_heading('5. Advanced Feature Insights', level=1)
    
    doc.add_heading('Seasonality-Adjusted Forecasts', level=2)
    doc.add_paragraph(
        "The 'SeasonalChurnPredictor' integrates monthly indexes to adjust risk scores based on industry buying patterns. "
        "It generates 3-month rolling forecasts identifying potential exit volumes by month."
    )
    
    doc.add_heading('Retailer Risk Linkage', level=2)
    doc.add_paragraph(
        "A unique feature of this project is 'Retailer Risk Mapping', which identifies retailers with high concentrations "
        "of high-risk plumbers. This allows for upstream interventions with partners rather than just individual customers."
    )
    
    doc.add_heading('Survival Modeling', level=2)
    doc.add_paragraph(
        "By treating a customer's journey as a lifespan, the system predicts the 'Median Days to Churn'. This allows "
        "management to prioritize customers who have the shortest remaining 'life' in the system."
    )
    
    # 6. Conclusion & Business Impact
    doc.add_heading('6. Conclusion & Business Impact', level=1)
    doc.add_paragraph(
        "The Churn Prediction Model empowers Skipper Pipes to transition from reactive to proactive retention. "
        "By identifying the 49 key retailers linked to high-risk plumber clusters and flagging 'drifting' high-value accounts, "
        "the sales team can focus resources where the potential for revenue recovery is highest."
    )
    
    doc.add_paragraph("\n\n--- End of Report ---")
    
    # Save the document
    report_name = "Skipper_Churn_Prediction_Project_Report.docx"
    doc.save(report_name)
    print(f"Report generated: {report_name}")

if __name__ == "__main__":
    create_churn_report()

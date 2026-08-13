"""
Report Generator Service
Generates professional plagiarism detection reports in various formats.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib import colors

from app.config import settings
from app.utils.helpers import get_timestamp, format_datetime, ensure_directory_exists


class ReportGenerator:
    """
    Generates plagiarism detection reports in multiple formats.
    """
    
    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        ensure_directory_exists(output_dir)
    
    def _get_classification_color(self, similarity: float) -> HexColor:
        """
        Get color based on similarity score.
        
        Args:
            similarity: Similarity percentage
            
        Returns:
            HexColor object
        """
        if similarity >= 80:
            return HexColor("#dc2626")  # Red
        elif similarity >= 60:
            return HexColor("#ea580c")  # Orange
        elif similarity >= 40:
            return HexColor("#f59e0b")  # Amber
        elif similarity >= 20:
            return HexColor("#84cc16")  # Lime
        else:
            return HexColor("#22c55e")  # Green
    
    def generate_pdf_report(
        self,
        analysis_data: Dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a PDF plagiarism report.
        
        Args:
            analysis_data: Analysis results dictionary
            filename: Optional custom filename
            
        Returns:
            Path to generated PDF file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plagiarism_report_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor("#1e40af"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor("#1e40af"),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=HexColor("#4b5563"),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Title
        elements.append(Paragraph("AI-POWERED PLAGIARISM DETECTION REPORT", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Document Information
        elements.append(Paragraph("Document Information", heading_style))
        
        doc_info_data = [
            ["Document Name:", analysis_data.get("document_name", "N/A")],
            ["Analysis Date:", analysis_data.get("analysis_date", "N/A")],
            ["Word Count:", str(analysis_data.get("word_count", 0))],
            ["Sentence Count:", str(analysis_data.get("sentence_count", 0))]
        ]
        
        doc_info_table = Table(doc_info_data, colWidths=[2*inch, 4*inch])
        doc_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor("#f3f4f6")),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb"))
        ]))
        
        elements.append(doc_info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Overall Similarity Score
        elements.append(Paragraph("Overall Similarity Analysis", heading_style))
        
        similarity = analysis_data.get("overall_similarity", 0)
        classification = analysis_data.get("classification", "Unknown")
        sim_color = self._get_classification_color(similarity)
        
        similarity_data = [
            ["Overall Similarity", f"{similarity:.2f}%"],
            ["Classification", classification]
        ]
        
        similarity_table = Table(similarity_data, colWidths=[3*inch, 3*inch])
        similarity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor("#f9fafb")),
            ('TEXTCOLOR', (0, 0), (0, -1), black),
            ('TEXTCOLOR', (1, 0), (1, 0), sim_color),
            ('TEXTCOLOR', (1, 1), (1, 1), sim_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor("#e5e7eb")),
            ('BOX', (0, 0), (-1, -1), 2, sim_color)
        ]))
        
        elements.append(similarity_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Component Scores
        elements.append(Paragraph("Similarity Component Scores", heading_style))
        
        scores = analysis_data.get("scores", {})
        weights = analysis_data.get("weights", {})
        
        component_data = [
            ["Method", "Score", "Weight", "Contribution"],
            [
                "TF-IDF",
                f"{scores.get('tfidf', 0):.2f}%",
                f"{weights.get('tfidf_weight', 0)*100:.0f}%",
                f"{scores.get('tfidf', 0) * weights.get('tfidf_weight', 0):.2f}%"
            ],
            [
                "N-Grams",
                f"{scores.get('ngram', 0):.2f}%",
                f"{weights.get('ngram_weight', 0)*100:.0f}%",
                f"{scores.get('ngram', 0) * weights.get('ngram_weight', 0):.2f}%"
            ],
            [
                "Fuzzy Matching",
                f"{scores.get('fuzzy', 0):.2f}%",
                f"{weights.get('fuzzy_weight', 0)*100:.0f}%",
                f"{scores.get('fuzzy', 0) * weights.get('fuzzy_weight', 0):.2f}%"
            ]
        ]
        
        component_table = Table(component_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f9fafb")])
        ]))
        
        elements.append(component_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Source Breakdown
        sources = analysis_data.get("sources", [])
        
        if sources:
            elements.append(Paragraph("Source Document Matches", heading_style))
            
            source_data = [["Source", "Similarity", "Matched Sentences"]]
            
            for source in sources[:10]:  # Limit to top 10
                source_data.append([
                    source.get("name", "Unknown"),
                    f"{source.get('similarity', 0):.2f}%",
                    str(source.get("matched_sentences", 0))
                ])
            
            source_table = Table(source_data, colWidths=[3*inch, 2*inch, 2*inch])
            source_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e40af")),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f9fafb")])
            ]))
            
            elements.append(source_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Matching Statistics
        elements.append(Paragraph("Match Statistics", heading_style))
        
        stats_data = [
            ["Total Sentence Matches:", str(analysis_data.get("total_matches", 0))],
            ["High Similarity Matches (≥80%):", str(analysis_data.get("high_similarity_matches", 0))],
            ["Reference Documents Analyzed:", str(len(sources))]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor("#f3f4f6")),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb"))
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Sample Sentence Matches
        sentence_matches = analysis_data.get("sentence_matches", [])
        
        if sentence_matches:
            elements.append(PageBreak())
            elements.append(Paragraph("Sample Sentence Matches", heading_style))
            elements.append(Paragraph(
                "Below are examples of sentences with high similarity to reference documents:",
                normal_style
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Show top 5 matches
            for idx, match in enumerate(sentence_matches[:5], 1):
                elements.append(Paragraph(f"<b>Match #{idx}</b>", subheading_style))
                
                match_info = [
                    ["Submitted:", match.get("submitted_sentence", "")[:200]],
                    ["Reference:", match.get("matched_sentence", "")[:200]],
                    ["Source:", match.get("source", "Unknown")],
                    ["Similarity:", f"{match.get('similarity', 0):.2f}%"]
                ]
                
                match_table = Table(match_info, colWidths=[1.2*inch, 5.3*inch])
                match_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), HexColor("#f3f4f6")),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb"))
                ]))
                
                elements.append(match_table)
                elements.append(Spacer(1, 0.15*inch))
        
        # Disclaimer
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Important Disclaimer", heading_style))
        disclaimer_text = """
        This similarity score indicates textual overlap and should be reviewed by a human 
        before concluding plagiarism. Common phrases and domain-specific terminology may 
        create false positives. The system uses NLP techniques (TF-IDF, N-grams, and Fuzzy 
        Matching) to detect potential similarities but does not prove plagiarism. Final 
        academic integrity decisions require professional human review and judgment.
        """
        elements.append(Paragraph(disclaimer_text, normal_style))
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def generate_json_report(
        self,
        analysis_data: Dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a JSON format report.
        
        Args:
            analysis_data: Analysis results dictionary
            filename: Optional custom filename
            
        Returns:
            Path to generated JSON file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plagiarism_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add metadata
        report_data = {
            "report_metadata": {
                "generated_at": get_timestamp(),
                "report_type": "plagiarism_detection",
                "version": "1.0"
            },
            "analysis_results": analysis_data
        }
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_report(
        self,
        analysis_data: Dict,
        report_format: str = "pdf",
        filename: Optional[str] = None
    ) -> str:
        """
        Generate report in specified format.
        
        Args:
            analysis_data: Analysis results dictionary
            report_format: Format for report ('pdf' or 'json')
            filename: Optional custom filename
            
        Returns:
            Path to generated report file
        """
        if report_format.lower() == "pdf":
            return self.generate_pdf_report(analysis_data, filename)
        elif report_format.lower() == "json":
            return self.generate_json_report(analysis_data, filename)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")


# Global report generator instance
report_generator = ReportGenerator()


# Convenience function
def create_plagiarism_report(
    analysis_data: Dict,
    report_format: str = "pdf",
    filename: Optional[str] = None
) -> str:
    """
    Create a plagiarism detection report.
    
    Args:
        analysis_data: Analysis results dictionary
        report_format: Format for report ('pdf' or 'json')
        filename: Optional custom filename
        
    Returns:
        Path to generated report file
    """
    return report_generator.generate_report(analysis_data, report_format, filename)

import pytest
from unittest.mock import patch, MagicMock
from src.utils.pdf_generator import generate_dashboard_pdf

@pytest.fixture
def mock_weasyprint():
    """Fixture to cleanly mock out the weasyprint HTML and PDF engine layers."""
    with patch("src.utils.pdf_generator.HTML") as mock_html_class:
        mock_html_instance = MagicMock()
        mock_html_class.return_value = mock_html_instance
        yield mock_html_class, mock_html_instance


def test_generate_dashboard_pdf_default_path(mock_weasyprint):
    """Verifies that the HTML engine initializes and saves to the default file destination path."""
    mock_class, mock_instance = mock_weasyprint
    
    # Act
    returned_path = generate_dashboard_pdf()
    
    # Assert
    assert returned_path == "world_x_desktop_snapshot.pdf"
    
    # Check that HTML class was initialized with the raw content string
    mock_class.assert_called_once()
    kwargs = mock_class.call_args[1]
    assert "string" in kwargs
    assert "WORLD-X: Asset Performance Analytics" in kwargs["string"]
    assert "₹24,315.20" in kwargs["string"]  # Verifies currency rendering holds intact
    
    # Check that it executed write_pdf targeting the correct default file location
    mock_instance.write_pdf.assert_called_once_with("world_x_desktop_snapshot.pdf")


def test_generate_dashboard_pdf_custom_path(mock_weasyprint):
    """Verifies that the HTML engine honors a custom file path assignment."""
    _, mock_instance = mock_weasyprint
    custom_destination = "/tmp/custom_location_report.pdf"
    
    # Act
    returned_path = generate_dashboard_pdf(output_path=custom_destination)
    
    # Assert
    assert returned_path == custom_destination
    mock_instance.write_pdf.assert_called_once_with(custom_destination)


def test_generate_dashboard_pdf_html_structure_content(mock_weasyprint):
    """Verifies that structural global market markers and CSS rules exist inside the template engine compilation."""
    mock_class, _ = mock_weasyprint
    
    # Act
    generate_dashboard_pdf()
    
    # Extract the payload passed into the weasyprint engine
    compiled_html_string = mock_class.call_args[1]["string"]
    
    # Structural Asset Assertions
    assert "<!DOCTYPE html>" in compiled_html_string
    assert "size: A4 portrait;" in compiled_html_string
    assert "background-color: #0f172a;" in compiled_html_string
    assert "Risk Warning:" in compiled_html_string
    assert "NIFTY 50" in compiled_html_string
    assert "Bitcoin Consolidation Breaks Out" in compiled_html_string

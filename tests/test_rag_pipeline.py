import pytest
from backend.services.classifier_service import QueryClassifierService


def test_query_classifier():
    cat, conf = QueryClassifierService.classify_query("What is the 75% attendance rule and condonation policy?")
    assert cat == "attendance"
    assert conf >= 0.7

    cat2, conf2 = QueryClassifierService.classify_query("Which companies visited DDU for IT placements and highest package?")
    assert cat2 == "placements"

    cat3, conf3 = QueryClassifierService.classify_query("How to apply for MYSY scholarship and tuition fee payment?")
    assert cat3 == "fees_scholarships"

    cat4, conf4 = QueryClassifierService.classify_query("How is SPI and CPI calculated with grade points?")
    assert cat4 == "examinations"

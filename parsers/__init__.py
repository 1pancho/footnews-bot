"""Parsers package for various news sources."""
from .sports_ru import SportsRuParser
from .championat import ChampionatParser
from .soccer_ru import SoccerRuParser

__all__ = ["SportsRuParser", "ChampionatParser", "SoccerRuParser"]

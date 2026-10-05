from typing import Literal

# Tipos reutilizables
Side = Literal["red", "blue"]
Gender = Literal["masculino", "femenino"]
MatchStatus = Literal["draft", "in_progress", "finished"]
CaptureMode = Literal["live", "video"]
Position = Literal["base", "escolta", "alero", "ala-pivot", "pivot"]
EventType = Literal["scoring", "rebound", "foul", "pass", "steal"]
ScoringType = Literal["tiro_libre", "tiro_de_cancha"]
PreviousAction = Literal["catch_and_shot", "dribbling", "pick_and_roll", "pick_and_pop"]
ReboundType = Literal["ofensivo", "defensivo"]
FoulType = Literal["personal", "en_tiro", "ofensiva", "tecnica", "antideportiva", "descalificante"]
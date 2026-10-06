"""Plain data classes shared by the analysis engine and the routes."""

from dataclasses import dataclass, field, asdict

PH_MIN, PH_MAX = 0.0, 14.0


@dataclass(frozen=True)
class Reading:
    """One measurement from DermaSense."""

    moisture: float   # percent, 0-100
    ph: float         # 0-14
    oiliness: float   # percent, 0-100

    def __post_init__(self):
        if not 0 <= self.moisture <= 100:
            raise ValueError("Moisture must be between 0 and 100%.")
        if not PH_MIN <= self.ph <= PH_MAX:
            raise ValueError("pH must be between 0 and 14.")
        if not 0 <= self.oiliness <= 100:
            raise ValueError("Oiliness must be between 0 and 100%.")

    @classmethod
    def from_form(cls, form):
        """Build a Reading from request.form, raising ValueError with a friendly message."""
        try:
            return cls(
                moisture=float(form["moisture"]),
                ph=float(form["ph"]),
                oiliness=float(form["oiliness"]),
            )
        except (KeyError, TypeError):
            raise ValueError("Please fill in all three readings.")
        except ValueError as error:
            # float() errors and our own range errors both land here
            text = str(error)
            if text.startswith("could not convert"):
                text = "Readings must be numbers."
            raise ValueError(text)


@dataclass
class SkinProfile:
    """The result of analysing a Reading."""

    skin_type: str
    moisture_level: str
    ph_status: str
    oil_level: str
    ingredients: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class User:
    id: int
    email: str
    created_at: str
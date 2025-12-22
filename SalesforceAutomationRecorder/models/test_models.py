"""
Data models for test execution
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TestAction:
    Order: int
    Element: str
    Action: str
    Value: str = ""
    Selector: str = ""
    DelayMs: int = 500
    IsNavigation: bool = False


@dataclass
class TestStep:
    Order: int
    StepName: str
    PageName: str
    PageUrl: str
    ActualUrl: str = ""
    Actions: List[TestAction] = field(default_factory=list)
    ElementsFound: int = 0


@dataclass
class TestScenario:
    ScenarioName: str
    Description: str
    Url: str
    Steps: List[TestStep] = field(default_factory=list)


@dataclass
class ActionResult:
    ActionOrder: int
    Element: str
    Action: str
    Timestamp: datetime
    Status: str = "Passed"
    ErrorMessage: Optional[str] = None
    ScreenshotPath: Optional[str] = None
    IsHighlighted: bool = False


@dataclass
class StepResult:
    StepOrder: int
    PageName: str
    StartTime: datetime
    EndTime: Optional[datetime] = None
    Status: str = "Passed"
    ErrorMessage: Optional[str] = None
    DurationMs: float = 0
    ActionResults: List[ActionResult] = field(default_factory=list)


@dataclass
class ConsoleLog:
    Type: str
    Text: str
    Timestamp: datetime
    Location: str = ""


@dataclass
class TestResult:
    ScenarioName: str
    StartTime: datetime
    EndTime: Optional[datetime] = None
    Status: str = "Passed"
    ErrorMessage: Optional[str] = None
    StackTrace: Optional[str] = None
    DurationMs: float = 0
    StepResults: List[StepResult] = field(default_factory=list)
    ConsoleLogs: List[ConsoleLog] = field(default_factory=list)

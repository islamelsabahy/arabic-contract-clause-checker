"""Clause checklist and risk patterns.

Patterns are written in ordinary Arabic spelling; they are normalised with the
same function as the contract text before matching, so alef/ya/ta-marbuta
variants and diacritics do not matter.
"""
from dataclasses import dataclass
from typing import Tuple

HIGH, MEDIUM, LOW = "high", "medium", "low"
SEVERITY_ORDER = {LOW: 1, MEDIUM: 2, HIGH: 3}


@dataclass(frozen=True)
class Clause:
    id: str
    en: str
    ar: str
    patterns: Tuple[str, ...]
    severity: str
    tip_en: str
    tip_ar: str
    kinds: Tuple[str, ...] = ("sale", "lease")


@dataclass(frozen=True)
class Risk:
    id: str
    en: str
    ar: str
    pattern: str
    severity: str
    tip_en: str
    tip_ar: str
    kinds: Tuple[str, ...] = ("sale", "lease")
    scope: str = "sentence"   # "paragraph" when the figure may sit in a neighbouring sentence


CLAUSES = (
    Clause("parties", "Parties identified (ID or commercial register)", "تحديد الأطراف (رقم قومي أو سجل تجاري)",
           (r"رقم قومي", r"بطاقة (?:الرقم القومي|رقم)", r"سجل تجاري", r"جواز سفر"), HIGH,
           "Name each party with national ID or commercial register number and address.",
           "اكتب اسم كل طرف ورقمه القومي أو سجله التجاري وعنوانه."),
    Clause("property", "Property description (area, location)", "وصف العقار (المساحة والموقع)",
           (r"مساح[ةه]", r"متر مربع", r"م2"), HIGH,
           "Describe the unit: number, floor, area in square metres, project and address.",
           "حدد الوحدة: رقمها والدور والمساحة بالمتر المربع والمشروع والعنوان."),
    Clause("price", "Price", "الثمن", (r"ثمن", r"إجمالي السعر", r"السعر الإجمالي", r"مبلغ وقدره"), HIGH,
           "State the total price in figures and words.", "اذكر الثمن الإجمالي بالأرقام والحروف.", ("sale",)),
    Clause("payment_schedule", "Payment schedule (down payment, installments)", "جدول السداد (المقدم والأقساط)",
           (r"مقدم", r"قسط", r"أقساط", r"يسدد", r"سداد"), HIGH,
           "Attach a dated schedule with amounts and the payment method.", "أرفق جدولاً بتواريخ وقيم الأقساط وطريقة السداد.", ("sale",)),
    Clause("delivery_date", "Delivery date", "موعد التسليم",
           (r"موعد التسليم", r"ميعاد التسليم", r"تاريخ التسليم", r"مدة التسليم", r"بتسليم", r"استلام الوحدة"), HIGH,
           "Give a fixed delivery date or a period counted from a defined event.",
           "حدد تاريخ تسليم ثابتاً أو مدة تُحسب من واقعة محددة.", ("sale",)),
    Clause("late_delivery_penalty", "Penalty for late delivery by the seller", "غرامة تأخر البائع في التسليم",
           (r"غرامة (?:ال)?تأخير", r"تعويض (?:عن )?(?:ال)?تأخير", r"شرط جزائي"), MEDIUM,
           "Add a delay compensation that applies to the seller, not only to the buyer.",
           "أضف تعويضاً عن تأخير التسليم يسري على البائع وليس على المشتري فقط.", ("sale",)),
    Clause("default_termination", "Default and termination terms", "الإخلال والفسخ",
           (r"فسخ", r"إخلال"), HIGH,
           "Say what counts as default, the cure period and what happens to money paid.",
           "اذكر ما يُعد إخلالاً ومهلة التصحيح ومصير المبالغ المسددة."),
    Clause("warranty", "Warranty / defects / maintenance", "الضمان والعيوب والصيانة",
           (r"ضمان", r"عيوب", r"صيانة"), MEDIUM,
           "State the warranty period and who handles defects and maintenance.",
           "حدد مدة الضمان ومن يتحمل العيوب والصيانة.", ("sale",)),
    Clause("registration", "Registration / notarisation", "التسجيل والشهر العقاري",
           (r"تسجيل", r"شهر عقاري", r"توثيق", r"تصديق"), MEDIUM,
           "State who registers the contract and who bears the fees.", "حدد من يتولى التسجيل ومن يتحمل الرسوم.", ("sale",)),
    Clause("rent", "Rent amount", "قيمة الإيجار", (r"أجرة", r"قيمة الإيجارية", r"قيمة الإيجار"), HIGH,
           "State the rent, the payment date and method.", "اذكر قيمة الإيجار وموعد وطريقة السداد.", ("lease",)),
    Clause("term", "Lease term", "مدة الإيجار", (r"مدة (?:الإيجار|العقد)", r"لمدة"), HIGH,
           "Give start and end dates.", "حدد تاريخ البداية والنهاية.", ("lease",)),
    Clause("purpose", "Permitted use", "الغرض من الاستعمال", (r"غرض", r"سكني", r"إدارياً", r"استعمال"), MEDIUM,
           "State the permitted use.", "اذكر الغرض المسموح به.", ("lease",)),
    Clause("deposit", "Security deposit", "مبلغ التأمين", (r"تأمين", r"وديعة"), MEDIUM,
           "State the amount and the conditions for refunding it.", "اذكر المبلغ وشروط رده.", ("lease",)),
    Clause("rent_increase", "Rent increase terms", "الزيادة الدورية", (r"زيادة (?:سنوية|دورية)", r"نسبة الزيادة"), MEDIUM,
           "State the increase as a fixed percentage and when it applies.", "اذكر الزيادة كنسبة محددة وموعد سريانها.", ("lease",)),
    Clause("sublet", "Subletting", "التأجير من الباطن", (r"من الباطن", r"التنازل عن الإيجار"), LOW,
           "Say whether subletting or assignment is allowed.", "وضّح هل يجوز التأجير من الباطن أو التنازل.", ("lease",)),
    Clause("return_condition", "Return of the premises", "تسليم العين عند الانتهاء",
           (r"إخلاء", r"تسليم العين", r"حالة جيدة", r"تسليم الوحدة"), MEDIUM,
           "Describe the condition on return and the handover procedure.", "صف حالة العين عند الإخلاء وإجراءات التسليم.", ("lease",)),
    Clause("notice", "Notice for termination", "الإخطار بالإنهاء", (r"إخطار", r"إنذار", r"إشعار"), MEDIUM,
           "State the notice period and form.", "حدد مدة وشكل الإخطار.", ("lease",)),
    Clause("governing_law", "Governing law and court / arbitration", "القانون الواجب التطبيق والاختصاص",
           (r"قانون المصري", r"اختصاص", r"محكمة", r"تحكيم", r"محاكم"), HIGH,
           "Name the governing law and the competent court or arbitration centre.",
           "حدد القانون الواجب التطبيق والمحكمة المختصة أو مركز التحكيم."),
    Clause("force_majeure", "Force majeure", "القوة القاهرة", (r"قوة قاهرة", r"ظروف طارئة", r"حادث مفاجئ"), LOW,
           "Define force majeure and its effect on deadlines.", "عرّف القوة القاهرة وأثرها على المواعيد."),
    Clause("notices_address", "Chosen address for notices", "الموطن المختار للمراسلات",
           (r"موطن مختار", r"مراسلات", r"إخطارات"), LOW,
           "Add a chosen address for notices.", "أضف موطناً مختاراً للإخطارات."),
    Clause("date", "Date of the contract", "تاريخ تحرير العقد",
           (r"تحرر هذا العقد", r"حرر هذا العقد", r"تحريراً في", r"حُرر في", r"حرر في", r"بتاريخ"), MEDIUM,
           "Date the contract.", "اكتب تاريخ تحرير العقد."),
    Clause("signatures", "Signatures", "التوقيعات", (r"توقيع", r"إمضاء", r"(?:^|[\s،,])و?وقع"), MEDIUM,
           "Leave signature blocks for every party.", "اترك مكاناً لتوقيع كل طرف."),
)

_NO_CAP = r"(?:%|٪|في المائة|بالمائة|بحد أقصى|لا (?:تزيد|تتجاوز|يزيد|يتجاوز)|الحد الأقصى)"

RISKS = (
    Risk("non_refundable", "Money paid is not refundable", "المبالغ المسددة لا تُسترد",
         r"لا (?:يرد|ترد|يسترد|تسترد)|غير قابل[ةه]? للاسترداد|لا يجوز استرداد|لا يحق (?:له|للطرف الثاني|للمشتري) (?:استرداد|المطالبة)",
         HIGH, "Blanket forfeiture can be challenged as an unfair penalty. Tie any deduction to a stated percentage and to proven default.",
         "مصادرة كل المبالغ قد يُطعن عليها كشرط جزائي مبالغ فيه. اربط أي خصم بنسبة محددة وبإخلال ثابت."),
    Risk("termination_no_notice", "Termination without notice or court ruling", "فسخ بدون إنذار أو حكم",
         r"(?:فسخ|إنهاء).{0,60}?(?:دون|بدون) (?:حاجة (?:إلى|الى) )?(?:إنذار|إعذار|تنبيه|حكم|اللجوء)|بدون (?:إنذار|إعذار|حكم)",
         HIGH, "Require a written notice and a cure period before termination.",
         "اشترط إنذاراً كتابياً ومهلة للتصحيح قبل الفسخ."),
    Risk("automatic_termination", "Contract terminates automatically", "فسخ تلقائي للعقد",
         r"مفسوخ[اً]? (?:من تلقاء نفسه|بقوة القانون|دون)|يفسخ (?:العقد )?(?:من تلقاء نفسه|بقوة القانون)",
         MEDIUM, "Check that automatic termination follows a notice and is mutual.", "تأكد أن الفسخ التلقائي يسبقه إنذار وأنه متبادل."),
    Risk("uncapped_penalty", "Penalty or compensation with no figure or cap", "غرامة أو تعويض بدون نسبة أو حد أقصى",
         r"^(?!.*(?:\d|" + _NO_CAP + r")).*(?:غرامة|شرط جزائي|تعويض)",
         MEDIUM, "Give the penalty as a percentage or amount with a maximum.",
         "اذكر الغرامة كنسبة أو مبلغ مع حد أقصى.",
         scope="paragraph"),
    Risk("waiver_of_rights", "A party waives rights broadly", "تنازل واسع عن الحقوق",
         r"يتنازل .{0,30}?عن (?:حقه|حقوقه|كافة|أي)|إبراء ذمة|تنازل نهائي",
         MEDIUM, "Limit any waiver to a specific right.", "اقصر التنازل على حق محدد."),
    Risk("sole_discretion", "Decision left to one party's sole discretion", "قرار بتقدير طرف واحد",
         r"(?:تقدير|إرادة|مشيئة) (?:الطرف الأول|الشركة|البائع|المؤجر)(?: وحده| المنفردة)?|(?:الطرف الأول|الشركة|البائع|المؤجر) وحده",
         MEDIUM, "Replace with an objective criterion or require mutual agreement.", "استبدلها بمعيار موضوعي أو اشترط اتفاق الطرفين."),
    Risk("open_delivery_extension", "Delivery date can be extended without limit", "تمديد موعد التسليم بدون حد",
         r"(?:ميعاد|موعد|مدة) التسليم.{0,80}?(?:قابل[ةه]? للتمديد|يجوز (?:للطرف الأول|للشركة|للبائع) (?:مد|تمديد|تأجيل))",
         MEDIUM, "Cap any extension (for example, 6 months) and tie it to force majeure.",
         "ضع حداً أقصى للتمديد (مثلاً 6 أشهر) واربطه بالقوة القاهرة.", ("sale",)),
    Risk("uncapped_rent_increase", "Rent increase with no percentage", "زيادة الإيجار بدون نسبة",
         r"^(?!.*(?:\d|" + _NO_CAP + r")).*(?:زيادة|رفع).{0,40}?(?:الأجرة|القيمة الإيجارية|الإيجار)",
         MEDIUM, "State the increase as a fixed percentage.", "اذكر الزيادة كنسبة ثابتة.", ("lease",), "paragraph"),
    Risk("blank_fields", "Unfilled blanks remain", "فراغات لم تُملأ",
         r"\.{4,}|_{3,}|…|\[\s*\]", LOW, "Fill or remove every blank before signing.", "املأ أو احذف كل الفراغات قبل التوقيع."),
)

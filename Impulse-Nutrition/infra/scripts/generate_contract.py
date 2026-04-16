#!/usr/bin/env python3
"""Generate Impulse Nutrition partnership contracts as PDF (2-column layout)."""

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from fpdf import FPDF

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "assets", "logo_impulse.jpeg")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "contracts")

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = os.path.join(FONT_DIR, "Arial.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Arial Bold.ttf")

HCS_NAME = "HAVEA COMMERCIAL SERVICES"
HCS_FORM = "Société par Actions Simplifiée"
HCS_SIEGE = "Parc d'activité Sud Loire, Boufféré, 85612 Montaigu-Vendée cedex"
HCS_RCS = "immatriculée au Registre du Commerce et des Sociétés de La Roche-sur-Yon sous le numéro 315249821"

# Page geometry
PAGE_W = 210
PAGE_H = 297
MARGIN_LEFT = 15
MARGIN_RIGHT = 15
MARGIN_TOP = 10
MARGIN_BOTTOM = 20
COL_GAP = 6
CONTENT_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
COL_W = (CONTENT_W - COL_GAP) / 2
COL_X = [MARGIN_LEFT, MARGIN_LEFT + COL_W + COL_GAP]
HEADER_Y = 54  # Y where columns start (below logo+title)
MAX_Y = PAGE_H - MARGIN_BOTTOM


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class ContractData:
    athlete_first_name: str
    athlete_last_name: str
    athlete_address: str
    contract_date: str
    contract_duration: int
    contract_type: str  # "dotation" or "paid"
    dotation_amount: float
    budget_amount: float
    affiliate_code: str
    min_stories: int
    min_reels: int
    gender: str
    party_term: str = "ATHLETE"  # "ATHLETE" or "INFLUENCEUR"
    fixed_amount: float = 0.0  # paid: rémunération fixe brute HT
    variable_amount: float = 10.0  # paid: commission par commande (€HT)
    billing_schedule: str = ""  # paid: ex "février / avril / juillet"
    dotation_code: str = ""  # paid: code dotation spécifique
    siren: str = ""  # optional: numéro SIREN/immatriculation
    custom_deliverables: str = ""  # paid: livrables détaillés (lignes séparées par |)
    renewal_threshold: int = 50  # dotation: seuil d'utilisations pour renouvellement auto

    @property
    def full_name(self) -> str:
        return f"{self.athlete_first_name} {self.athlete_last_name.upper()}"

    @property
    def domicilie(self) -> str:
        return "Domiciliée" if self.gender == "F" else "Domicilié"

    @property
    def denommee(self) -> str:
        return "dénommée" if self.gender == "F" else "dénommé"

    @property
    def term(self) -> str:
        return self.party_term

    @property
    def term_article(self) -> str:
        """l'ATHLETE or l'INFLUENCEUR"""
        return f"l'{self.party_term}"

    @property
    def term_article_cap(self) -> str:
        """L'ATHLETE or L'INFLUENCEUR (for start of sentence)"""
        return f"L'{self.party_term}"

    @property
    def output_filename(self) -> str:
        parts = self.contract_date.split("/")
        if len(parts) == 3:
            date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        return f"Contract_{self.athlete_first_name}_{self.athlete_last_name}_{date_str}.pdf"

    @property
    def discount_url(self) -> str:
        return f"https://impulse-nutrition.fr/discount/{self.affiliate_code}"

    @property
    def effective_dotation_code(self) -> str:
        """Return dotation code: explicit or auto-generated from first name."""
        if self.dotation_code:
            return self.dotation_code
        return self.athlete_first_name.upper().replace(" ", "").replace("-", "") + "DOTATION"

    @property
    def deliverables_list(self) -> list:
        """Parse custom_deliverables string into a list."""
        if not self.custom_deliverables:
            return []
        return [d.strip() for d in self.custom_deliverables.split("|") if d.strip()]


# ---------------------------------------------------------------------------
# Two-column PDF
# ---------------------------------------------------------------------------

class ContractPDF(FPDF):
    """PDF with flowing 2-column layout."""

    def __init__(self, data: ContractData):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.data = data
        self.set_auto_page_break(auto=False)
        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)

        # Register Unicode TTF fonts
        self.add_font("F", "", FONT_REGULAR)
        self.add_font("F", "B", FONT_BOLD)
        self.set_font("F", "", 8.5)

        # Column state
        self.col = 0  # 0=left, 1=right
        self.col_y = HEADER_Y  # current Y in the active column
        self.first_page_content_y = HEADER_Y  # set after parties table on page 1
        self.is_first_page = True
        self.total_pages = 0  # set after building

    def header(self):
        """Logo + title on every page."""
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=70.5, y=8.5, w=69)
        else:
            self.set_font("F", "B", 16)
            self.set_xy(MARGIN_LEFT, 10)
            self.cell(CONTENT_W, 8, "IMPULSE NUTRITION", align="C")
        self.set_font("F", "", 8.5)

    def footer(self):
        """Page number footer."""
        self.set_y(-12)
        self.set_font("F", "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(CONTENT_W, 5, f"Page {self.page_no()}/{{nb}}", align="C")
        self.set_text_color(0, 0, 0)

    def _cur_x(self):
        return COL_X[self.col]

    def _col_start_y(self):
        """Y where columns start on the current page."""
        if self.is_first_page:
            return self.first_page_content_y
        return HEADER_Y

    def _ensure_space(self, needed_h):
        """If not enough space in current column, switch column or page."""
        if self.col_y + needed_h > MAX_Y:
            if self.col == 0:
                # Switch to right column on same page
                self._left_col_bottom = self.col_y  # track for signature
                self.col = 1
                self.col_y = self._col_start_y()
            else:
                # New page, back to left column
                self.add_page()
                self.is_first_page = False
                self.col = 0
                self.col_y = HEADER_Y

    def _force_column_break(self):
        """Force switch to right column (or new page if already in right)."""
        if self.col == 0:
            self._left_col_bottom = self.col_y  # track for signature placement
            self.col = 1
            self.col_y = self._col_start_y()
        else:
            self.add_page()
            self.is_first_page = False
            self.col = 0
            self.col_y = HEADER_Y

    def _write_block(self, text, font_style="", font_size=8.5, align="J", line_h=4.0):
        """Write a multi_cell block in the current column, handling overflow."""
        self.set_font("F", font_style, font_size)
        h = self._measure_multicell(text, font_style, font_size, COL_W, line_h)
        self._ensure_space(h)
        self.set_xy(self._cur_x(), self.col_y)
        self.multi_cell(COL_W, line_h, text, align=align)
        self.col_y = self.get_y()

    def _measure_multicell(self, text, font_style, font_size, w, line_h):
        """Measure the height a multi_cell would take without drawing."""
        self.set_font("F", font_style, font_size)
        result = self.multi_cell(w, line_h, text, dry_run=True, output="LINES")
        return len(result) * line_h

    def _write_article_header(self, number, title):
        """Write bold article header inline."""
        header = f"Article {number} — {title}"
        self.set_font("F", "B", 8.5)
        self._ensure_space(5)
        self.set_xy(self._cur_x(), self.col_y)
        self.cell(COL_W, 4.0, header, new_x="LEFT", new_y="NEXT")
        self.col_y = self.get_y()

    def _write_article(self, number, title, body):
        """Write a full article (header + body), keeping them together."""
        # Measure total height to avoid orphan headers
        header = f"Article {number} — {title}"
        header_h = 4.0
        body_h = self._measure_multicell(body, "", 8.5, COL_W, 4.0)
        # Ensure at least header + first ~2 lines of body fit together
        min_together = header_h + min(body_h, 12)
        self._ensure_space(min_together)
        self._write_article_header(number, title)
        self._write_block(body, font_style="", font_size=8.5, align="J")
        self.col_y += 3  # more breathing room between articles

    def _write_bullet(self, text, indent=3):
        """Write a bullet point with hanging indent (wrap aligns after dash)."""
        self.set_font("F", "", 8.5)
        dash_w = self.get_string_width("- ")
        text_w = COL_W - indent - dash_w
        h = self._measure_multicell(text, "", 8.5, text_w, 4.0)
        self._ensure_space(h)
        base_x = self._cur_x()
        self.set_xy(base_x + indent, self.col_y)
        self.cell(dash_w, 4.0, "- ", new_x="END", new_y="TOP")
        self.set_xy(base_x + indent + dash_w, self.col_y)
        self.multi_cell(text_w, 4.0, text, align="L")
        self.col_y = self.get_y()

    def _spacing(self, h=2):
        self.col_y += h


# ---------------------------------------------------------------------------
# Article text generators
# ---------------------------------------------------------------------------

def article_1(d: ContractData) -> str:
    return (
        f"Le présent contrat a pour objet de définir les obligations réciproques "
        f"des parties dans le cadre d'une opération de partenariat entre {d.term_article} "
        f'et HCS, aux fins de promotion de la marque « IMPULSE Nutrition ».'
    )


def article_2(d: ContractData) -> str:
    duration_text = f"{d.contract_duration} mois"
    base = (
        f"Le présent contrat est conclu pour une durée déterminée de {duration_text} "
        f"à compter de sa Date d'effet."
    )
    if d.contract_type == "dotation":
        renewal = (
            f" Le présent contrat pourra être automatiquement renouvelé pour une durée de "
            f"{duration_text}, dès lors que le nombre d'utilisation du code d'affiliation "
            f"sera utilisé {d.renewal_threshold} fois ou plus sur la durée du présent "
            f"contrat. A défaut d'atteinte de cet objectif, les parties seront considérées "
            f"libres de tous engagements à l'expiration du contrat."
        )
    else:  # paid
        renewal = (
            " Le présent contrat pourra être renouvelé pour une autre durée convenue entre "
            "les parties et dont les modalités seront fixées par voie d'avenant. A défaut "
            "d'accord sur les conditions d'un renouvellement, les parties seront considérées "
            "libres de tous engagements à l'expiration du contrat."
        )
    termination = (
        " Le contrat peut être résilié à tout moment par l'une ou l'autre des "
        "parties avec un préavis d'un mois."
    )
    return base + renewal + termination


def article_3(d: ContractData) -> str:
    base = (
        "En contrepartie de l'exécution de ses engagements contractuels, HCS s'engage à "
    )
    order_method = (
        f"La commande sera à passer directement par {d.term_article} "
        f"via le code {d.effective_dotation_code}, une fois par mois."
    )
    return (
        base +
        f"fournir à {d.term_article} les compléments alimentaires nécessaires à sa consommation "
        f"personnelle. A cet effet, {d.term_article} se verra attribuer une dotation mensuelle "
        f"composée de compléments alimentaires pour une valeur totale de "
        f"{int(d.dotation_amount)}€TTC/mois pendant la durée du présent contrat. "
        + order_method
    )


def article_5(d: ContractData) -> str:
    if d.contract_type == "paid":
        duration_text = f"{d.contract_duration} ({_nombre_lettres(d.contract_duration)}) mois"
    else:
        duration_text = "2 (deux) ans"
    return (
        f"{d.term_article_cap} cède à HCS, dans les limites et conditions précisées ci-après, "
        f"les droits d'auteur de nature patrimoniale définis ci-après, portant sur les "
        f"Contenus. Cette cession est consentie pour le monde entier et pour une durée "
        f"de {duration_text}."
    )


def _nombre_lettres(n: int) -> str:
    """Convert small numbers to French words."""
    mots = {1: "un", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq", 6: "six",
            7: "sept", 8: "huit", 9: "neuf", 10: "dix", 11: "onze", 12: "douze",
            18: "dix-huit", 24: "vingt-quatre", 36: "trente-six"}
    return mots.get(n, str(n))


def article_5_para2():
    return (
        "La présente cession de droits d'auteur portant sur les Contenus comprend les "
        "droits de reproduction, de représentation, et de communication, qui se traduit "
        "notamment par le droit de reposter le ou les Contenu(s) et couvre, sans limitation "
        "de nombre, tout usage et toutes exploitations directes et/ou indirectes, sous "
        "toutes formes et selon toutes modalités."
    )


def article_5_para3():
    return (
        "L'ensemble des droits susvisés cédés à HCS le sont aux seules fins de :"
    )


ARTICLE_5_BULLETS = [
    "Communication commerciale ou non, sur tous types de supports et en tous formats "
    "(notamment sites internet, réseaux et médias sociaux, presse, évènementiel, etc.) ;",
    "Promotion/publicité, commerciale ou non, sur tous types de supports et en tous formats "
    "(notamment sites internet, réseaux et médias sociaux, presse, évènementiel, etc.) ;",
    "Communication interne et/ou institutionnelle (et notamment évènementiel) ;",
]


def article_6(d: ContractData) -> str:
    if d.contract_type == "paid":
        duration_text = f"{d.contract_duration} ({_nombre_lettres(d.contract_duration)}) mois"
    else:
        duration_text = ("toute la durée du contrat ainsi qu'un an après la rupture du "
                         "dernier contrat non renouvelé")
    return (
        f"{d.term_article_cap} donne l'autorisation à HCS d'utiliser son image et sa prestation "
        f"apparaissant sur les Contenus pour les mêmes finalités énoncées à l'article 5 "
        f"sur la cession de droit d'auteur. Cette autorisation est donnée pour le monde entier "
        f"et pendant {duration_text}."
    )


def article_remuneration(d: ContractData) -> str:
    """Article 7 for paid contracts only."""
    text = (
        f"En sus de la dotation de produits définie à l'article 3, {d.term_article} "
        f"percevra, au titre de la création et de la publication des Contenus, une "
        f"rémunération de {int(d.fixed_amount):,}€ euros bruts H.T. Ce montant inclus "
        f"la rémunération de l'autorisation de droit à l'image ainsi que la cession des "
        f"droits sur le Contenu au bénéfice de HCS."
    ).replace(",", " ")

    text += (
        f"\n\nLa rémunération interviendra uniquement une fois le Contenu créé, validé "
        f"par HCS et publié sur le Réseau social de {d.term_article}"
    )
    if d.billing_schedule:
        text += f", et sera versée en plusieurs temps (facturation {d.billing_schedule})."
    else:
        text += "."

    if d.variable_amount > 0:
        text += (
            f"\n\n{d.term_article_cap} pourra bénéficier d'une rémunération variable "
            f"complémentaire liée à l'affiliation correspondant à {int(d.variable_amount)}€HT "
            f"par commande passée par un nouveau client utilisant le code affilié défini."
        )

    text += (
        f"\n\nHCS réglera la facture produite et transmise par {d.term_article} "
        f"en bonne et due forme, dans les 60 jours à compter de sa date d'émission. "
        f"Ce règlement sera effectué, par virement, sur le compte bancaire dont les "
        f"coordonnées bancaires ont été communiquées à HCS par {d.term_article}."
    )
    return text


def article_droit_applicable():
    return (
        "Le Contrat est soumis au droit français. Toute contestation portant sur la validité, "
        "l'interprétation ou l'exécution du présent contrat sera soumise, à défaut d'accord "
        "amiable préalable entre les Parties, aux tribunaux compétents de Paris."
    )


# ---------------------------------------------------------------------------
# Build the full PDF
# ---------------------------------------------------------------------------

def build_contract(data: ContractData) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf = ContractPDF(data)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- Full-width header ---
    pdf.set_font("F", "B", 13)
    pdf.set_xy(MARGIN_LEFT, 42)
    pdf.cell(CONTENT_W, 7, "CONTRAT DE PARTENARIAT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # Thin separator line
    sep_y = pdf.get_y() + 1
    pdf.set_draw_color(180, 180, 180)
    pdf.line(MARGIN_LEFT + 30, sep_y, MARGIN_LEFT + CONTENT_W - 30, sep_y)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("F", "", 8.5)
    pdf.set_x(MARGIN_LEFT)
    pdf.cell(CONTENT_W, 5, f"Le contrat (Contrat) est conclu et prend effet le {data.contract_date},", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # --- Parties table (side-by-side with borders) ---
    y_table_top = pdf.get_y()
    pad = 1  # inner padding

    # Left column: HCS (content only, no "D'une part" yet)
    pdf.set_xy(COL_X[0] + pad, y_table_top + pad)
    pdf.set_font("F", "B", 8.5)
    pdf.cell(COL_W - 2 * pad, 4, "Entre :", new_x="LEFT", new_y="NEXT")
    pdf.set_x(COL_X[0] + pad)
    pdf.multi_cell(COL_W - 2 * pad, 3.8, f"{HCS_NAME}, {HCS_FORM}", align="L")
    pdf.set_x(COL_X[0] + pad)
    pdf.set_font("F", "", 8.5)
    pdf.multi_cell(COL_W - 2 * pad, 3.8, f"dont le siège social est situé {HCS_SIEGE}, {HCS_RCS},", align="L")
    pdf.set_x(COL_X[0] + pad)
    pdf.multi_cell(COL_W - 2 * pad, 3.8, 'Ci-après dénommée « HCS »,', align="L")
    y_left_content_end = pdf.get_y()

    # Right column: Athlete (content only, no "D'autre part" yet)
    pdf.set_xy(COL_X[1] + pad, y_table_top + pad)
    pdf.set_font("F", "B", 8.5)
    pdf.cell(COL_W - 2 * pad, 4, "Et,", new_x="LEFT", new_y="NEXT")
    pdf.set_xy(COL_X[1] + pad, pdf.get_y())
    pdf.multi_cell(COL_W - 2 * pad, 3.8, data.full_name, align="L")
    pdf.set_x(COL_X[1] + pad)
    pdf.set_font("F", "", 8.5)
    if data.siren:
        pdf.multi_cell(COL_W - 2 * pad, 3.8, f"Immatriculée sous le numéro : {data.siren}", align="L")
        pdf.set_x(COL_X[1] + pad)
    pdf.multi_cell(COL_W - 2 * pad, 3.8, f"{data.domicilie} au : {data.athlete_address}", align="L")
    pdf.set_x(COL_X[1] + pad)
    pdf.multi_cell(COL_W - 2 * pad, 3.8, f'Ci-après {data.denommee} l\'« {data.term} »,', align="L")
    y_right_content_end = pdf.get_y()

    # Align "D'une part" and "D'autre part" at the same Y (below the tallest column)
    y_label = max(y_left_content_end, y_right_content_end) + 2
    pdf.set_font("F", "B", 8.5)
    pdf.set_xy(COL_X[0] + pad, y_label)
    pdf.cell(COL_W - 2 * pad, 5, "D'une part,", align="C")
    pdf.set_xy(COL_X[1] + pad, y_label)
    pdf.cell(COL_W - 2 * pad, 5, "D'autre part,", align="C")

    y_table_bottom = y_label + 5 + pad

    # Draw table borders
    table_w = CONTENT_W
    pdf.line(MARGIN_LEFT, y_table_top, MARGIN_LEFT + table_w, y_table_top)
    pdf.line(MARGIN_LEFT, y_table_bottom, MARGIN_LEFT + table_w, y_table_bottom)
    pdf.line(MARGIN_LEFT, y_table_top, MARGIN_LEFT, y_table_bottom)
    pdf.line(MARGIN_LEFT + table_w, y_table_top, MARGIN_LEFT + table_w, y_table_bottom)
    pdf.line(COL_X[1] - COL_GAP / 2, y_table_top, COL_X[1] - COL_GAP / 2, y_table_bottom)

    # "Ci-après désignés..." centered full-width
    pdf.set_xy(MARGIN_LEFT, y_table_bottom + 2)
    pdf.set_font("F", "", 8.5)
    pdf.multi_cell(CONTENT_W, 4, 'Ci-après désignés ensemble par les « Parties » et individuellement par la « Partie ».', align="C")
    pdf.ln(2)

    # --- Start 2-column flowing content ---
    pdf.col = 0
    pdf.col_y = pdf.get_y()
    pdf.first_page_content_y = pdf.col_y  # right column starts here too

    art_num = 1

    # Article 1
    pdf._write_article(art_num, "OBJET DU CONTRAT", article_1(data))
    art_num += 1

    # Article 2
    pdf._write_article(art_num, "DUREE DU CONTRAT", article_2(data))
    art_num += 1

    # Article 3
    pdf._write_article(art_num, "OBLIGATIONS DE HCS", article_3(data))
    art_num += 1

    # Article 4 — Obligations
    pdf._write_article_header(art_num, f"OBLIGATIONS DE {data.term_article.upper()}")
    if data.deliverables_list:
        # Paid: detailed custom deliverables
        intro = (
            f"En contrepartie de l'exécution par HCS de ses obligations, {data.term_article} s'engage "
            f'à assurer la promotion de la gamme « IMPULSE Nutrition » sur ses réseaux sociaux, '
            f"et plus précisément en délivrant les livrables suivants :"
        )
        pdf._write_block(intro)
        pdf._spacing(1)
        for deliverable in data.deliverables_list:
            pdf._write_bullet(deliverable)
    else:
        # Dotation: simple stories + reels
        intro = (
            f"En contrepartie de l'exécution par HCS de ses obligations, {data.term_article} s'engage "
            f'à assurer la promotion de la gamme « IMPULSE Nutrition » sur ses réseaux sociaux, '
            f"et plus précisément en postant au moins {data.min_stories} stories et "
            f"{data.min_reels} réel ou post sur son compte Instagram par mois."
        )
        pdf._write_block(intro)
    pdf._spacing(1)
    pdf._write_block("Les publications contiendront :", align="L")
    pdf._write_bullet(f'Le code affilié "{data.affiliate_code}" ;')
    pdf._write_bullet("La mention du compte @impulse_nutrition_fr ;")
    pdf._write_bullet(
        f"Le lien suivant en swipe-up : {data.discount_url}"
    )
    pdf._write_bullet('Le visuel d\'un produit « Impulse Nutrition » au minimum.')
    pdf._spacing(1)
    pdf._write_block(
        f"{data.term_article_cap} s'engage à inclure de façon cohérente les compléments "
        f'« IMPULSE Nutrition » au sein de ses publications ainsi que le code '
        f"affilié qui lui a été attribué.",
        align="J",
    )
    pdf._spacing(1)
    pdf._write_block(
        f"Toute collaboration de {data.term_article.upper()} avec une autre marque de compléments "
        "alimentaires pendant la durée du contrat devra être préalablement approuvée par HCS.",
        align="J",
    )
    pdf._spacing(2)
    art_num += 1

    # Article 5
    pdf._write_article_header(art_num, "PROPRIETE INTELLECTUELLE")
    pdf._write_block(article_5(data))
    pdf._spacing(1)
    pdf._write_block(article_5_para2())
    pdf._spacing(1)
    pdf._write_block(article_5_para3(), align="L")
    for bullet in ARTICLE_5_BULLETS:
        pdf._write_bullet(bullet)
    pdf._spacing(2)
    art_num += 1

    # --- Tail articles with last-page balance (two-pass midpoint split) ---
    # Collect the tail: Art 6, (paid only) Art 7 Rémunération paragraphs, Art droit applicable.
    # Dry-measure all blocks, compute cumulative heights, decide midpoint split if we land
    # on a non-first page in the left column — so col 0 and col 1 end up visually balanced.
    art6_body = article_6(data)
    art_droit_body = article_droit_applicable()

    # Each tail block: (kind, payload, height). kind ∈ {"article", "header", "para"}.
    tail_blocks: list = []
    tail_blocks.append(("article", ("AUTORISATION DROIT A L'IMAGE", art6_body),
                        4.0 + pdf._measure_multicell(art6_body, "", 8.5, COL_W, 4.0) + 3))

    if data.contract_type == "paid":
        tail_blocks.append(("header", "REMUNERATION", 4.0))
        for para in [p.strip() for p in article_remuneration(data).split("\n\n") if p.strip()]:
            tail_blocks.append(("para", para,
                                pdf._measure_multicell(para, "", 8.5, COL_W, 4.0) + 3))
        # spacing added after art 7 before art droit
        tail_blocks.append(("spacing", 2, 2))

    tail_blocks.append(("article", ("DROIT APPLICABLE - ATTRIBUTION DE JURIDICTION", art_droit_body),
                        4.0 + pdf._measure_multicell(art_droit_body, "", 8.5, COL_W, 4.0) + 3))

    # Trigger any pending column/page break BEFORE measuring state, so the decision below
    # reflects where the tail will actually start rendering (and not the position at the
    # end of Art 5 which may still be in the right column of the previous page).
    if tail_blocks:
        pdf._ensure_space(tail_blocks[0][2])

    # Decide split: only if we're on a non-first page, in col 0 (i.e. tail spilled onto a
    # fresh page with col 1 otherwise empty). Otherwise let natural flow handle it.
    break_after = None
    if not pdf.is_first_page and pdf.col == 0:
        total_h = sum(h for _, _, h in tail_blocks)
        midpoint = total_h / 2
        accum = 0
        for i, (_, _, h) in enumerate(tail_blocks):
            accum += h
            if accum >= midpoint:
                break_after = i + 1
                break

    # Render the tail, forcing a column break at the computed midpoint
    for i, (kind, payload, _) in enumerate(tail_blocks):
        if kind == "article":
            title, body = payload
            pdf._write_article(art_num, title, body)
            art_num += 1
        elif kind == "header":
            pdf._write_article_header(art_num, payload)
            art_num += 1
        elif kind == "para":
            pdf._write_block(payload)
            pdf._spacing(1)
        elif kind == "spacing":
            pdf._spacing(payload)

        if break_after == i + 1 and pdf.col == 0:
            pdf._force_column_break()

    # --- Signature block (below both columns) ---
    # Track the bottom of both columns to place signature below the tallest
    if pdf.col == 1:
        # We're in right column; left col overflowed (went to MAX_Y or we forced a break)
        # Left col bottom is wherever content stopped before the break
        right_bottom = pdf.col_y
        # Left col could have gone up to MAX_Y (natural overflow) or less (forced break)
        # Use a tracked value if available, otherwise assume content extends further in left
        left_bottom = getattr(pdf, '_left_col_bottom', right_bottom)
        sig_y = max(left_bottom, right_bottom) + 12
    else:
        sig_y = pdf.col_y + 12
    if sig_y + 35 > MAX_Y:
        pdf.add_page()
        pdf.is_first_page = False
        sig_y = HEADER_Y

    # Separator line
    pdf.set_draw_color(120, 120, 120)
    pdf.line(MARGIN_LEFT, sig_y - 2, MARGIN_LEFT + CONTENT_W, sig_y - 2)
    pdf.set_draw_color(0, 0, 0)

    sig_line_w = COL_W - 30  # width of the signature line

    # Left: Athlete
    pdf.set_font("F", "B", 8.5)
    pdf.set_xy(MARGIN_LEFT, sig_y)
    pdf.cell(COL_W, 5, f"L'{data.term}", new_x="LEFT", new_y="NEXT")
    pdf.set_x(MARGIN_LEFT)
    pdf.set_font("F", "", 8.5)
    pdf.cell(COL_W, 5, f"Nom : {data.full_name}", new_x="LEFT", new_y="NEXT")
    pdf.set_x(MARGIN_LEFT)
    date_line_y = pdf.get_y()
    pdf.cell(COL_W, 5, "Date :", new_x="LEFT", new_y="NEXT")
    pdf.line(MARGIN_LEFT + 15, date_line_y + 4.5, MARGIN_LEFT + 15 + sig_line_w, date_line_y + 4.5)
    pdf.set_x(MARGIN_LEFT)
    pdf.ln(3)
    sig_line_y = pdf.get_y()
    pdf.cell(COL_W, 5, "Signature :", new_x="LEFT", new_y="NEXT")
    pdf.line(MARGIN_LEFT + 22, sig_line_y + 4.5, MARGIN_LEFT + 22 + sig_line_w - 7, sig_line_y + 4.5)

    # Right: HCS
    pdf.set_font("F", "B", 8.5)
    pdf.set_xy(COL_X[1], sig_y)
    pdf.cell(COL_W, 5, "HCS", new_x="LEFT", new_y="NEXT")
    pdf.set_font("F", "", 8.5)
    pdf.set_xy(COL_X[1], sig_y + 5)
    pdf.cell(COL_W, 5, f"Représentée par : ____________________", new_x="LEFT", new_y="NEXT")
    pdf.set_xy(COL_X[1], date_line_y)
    pdf.cell(COL_W, 5, "Date :", new_x="LEFT", new_y="NEXT")
    pdf.line(COL_X[1] + 15, date_line_y + 4.5, COL_X[1] + 15 + sig_line_w, date_line_y + 4.5)
    pdf.set_xy(COL_X[1], sig_line_y)
    pdf.cell(COL_W, 5, "Signature :", new_x="LEFT", new_y="NEXT")
    pdf.line(COL_X[1] + 22, sig_line_y + 4.5, COL_X[1] + 22 + sig_line_w - 7, sig_line_y + 4.5)

    output_path = os.path.join(OUTPUT_DIR, data.output_filename)
    pdf.output(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def prompt_input(label: str, default: str = "") -> str:
    if default:
        val = input(f"{label} [{default}] : ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"{label} : ").strip()
            if val:
                return val
            print("  (Ce champ est requis)")


def interactive_cli() -> ContractData:
    print("\n=== Générateur de contrat Impulse Nutrition ===\n")

    first_name = prompt_input("Prénom")
    last_name = prompt_input("Nom")
    address = prompt_input("Adresse complète")
    date = prompt_input("Date d'effet (JJ/MM/AAAA)", datetime.now().strftime("%d/%m/%Y"))
    duration = int(prompt_input("Durée en mois", "12"))

    print("\nTypes de contrat :")
    print("  1. dotation — Dotation mensuelle de produits")
    print("  2. paid     — Contrat payant (rémunération + dotation)")
    type_choice = prompt_input("Type (1/2 ou nom)")
    type_map = {"1": "dotation", "2": "paid"}
    contract_type = type_map.get(type_choice, type_choice)

    party_term = prompt_input("Terme (ATHLETE/INFLUENCEUR)", "ATHLETE").upper()

    dotation_amount = float(prompt_input("Montant dotation €TTC/mois", "0"))
    code = prompt_input("Code d'affiliation (ex: AUGUSTIN)")

    fixed_amount = 0.0
    variable_amount = 10.0
    billing_schedule = ""
    budget_amount = 0.0
    dotation_code = ""
    custom_deliverables = ""
    siren = ""

    if contract_type == "paid":
        fixed_amount = float(prompt_input("Rémunération fixe brute HT (€)"))
        variable_amount = float(prompt_input("Commission variable par commande (€HT)", "10"))
        budget_amount = fixed_amount + dotation_amount * duration
        billing_schedule = prompt_input("Calendrier facturation (ex: février / avril / juillet)", "")
        siren = prompt_input("Numéro SIREN (ou vide)", "")
        custom_deliverables = prompt_input(
            "Livrables détaillés (séparés par | ) ou vide pour mode simple", ""
        )

    dotation_code_input = prompt_input("Code dotation spécifique (ou vide)", "")

    stories = int(prompt_input("Stories minimum/mois", "3"))
    reels = int(prompt_input("Réels ou posts minimum/mois", "1"))
    gender = prompt_input("Genre (M/F)", "M").upper()

    return ContractData(
        athlete_first_name=first_name,
        athlete_last_name=last_name,
        athlete_address=address,
        contract_date=date,
        contract_duration=duration,
        contract_type=contract_type,
        dotation_amount=dotation_amount,
        budget_amount=budget_amount,
        affiliate_code=code,
        min_stories=stories,
        min_reels=reels,
        gender=gender,
        party_term=party_term,
        fixed_amount=fixed_amount,
        variable_amount=variable_amount,
        billing_schedule=billing_schedule,
        dotation_code=dotation_code_input,
        siren=siren,
        custom_deliverables=custom_deliverables,
    )


# ---------------------------------------------------------------------------
# Argparse mode
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate Impulse Nutrition contract PDF")
    p.add_argument("--first-name", required=True)
    p.add_argument("--last-name", required=True)
    p.add_argument("--address", required=True)
    p.add_argument("--date", default=datetime.now().strftime("%d/%m/%Y"))
    p.add_argument("--duration", type=int, default=12)
    p.add_argument("--type", required=True, choices=["dotation", "paid"])
    p.add_argument("--dotation-amount", type=float, default=0)
    p.add_argument("--budget-amount", type=float, default=0)
    p.add_argument("--code", required=True)
    p.add_argument("--stories", type=int, default=3)
    p.add_argument("--reels", type=int, default=1)
    p.add_argument("--gender", default="M", choices=["M", "F"])
    p.add_argument("--term", default="ATHLETE", choices=["ATHLETE", "INFLUENCEUR"])
    p.add_argument("--fixed-amount", type=float, default=0)
    p.add_argument("--variable-amount", type=float, default=10)
    p.add_argument("--billing-schedule", default="")
    p.add_argument("--dotation-code", default="")
    p.add_argument("--siren", default="")
    p.add_argument("--deliverables", default="", help="Pipe-separated list of custom deliverables")
    p.add_argument("--renewal-threshold", type=int, default=50,
                   help="Dotation: nombre d'utilisations du code affilié pour renouvellement auto")
    p.add_argument(
        "--upload-drive",
        action="store_true",
        help="Upload the generated PDF to the Drive folder InfluenceContract.",
    )
    p.add_argument(
        "--update-sheet",
        action="store_true",
        help="Write the Drive link into the corresponding Sheet row "
             "(Suivi_Dot col AE for dotation, Suivi_Paid col AM for paid). "
             "Implies --upload-drive.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the PDF but skip Drive upload and Sheet write.",
    )
    return p


def parse_args() -> Tuple["ContractData", argparse.Namespace]:
    args = _build_arg_parser().parse_args()
    return _args_to_data(args), args


def _args_to_data(args: argparse.Namespace) -> "ContractData":
    return ContractData(
        athlete_first_name=args.first_name,
        athlete_last_name=args.last_name,
        athlete_address=args.address,
        contract_date=args.date,
        contract_duration=args.duration,
        contract_type=args.type,
        dotation_amount=args.dotation_amount,
        budget_amount=args.budget_amount,
        affiliate_code=args.code,
        min_stories=args.stories,
        min_reels=args.reels,
        gender=args.gender,
        party_term=args.term,
        fixed_amount=args.fixed_amount,
        variable_amount=args.variable_amount,
        billing_schedule=args.billing_schedule,
        dotation_code=args.dotation_code,
        siren=args.siren,
        custom_deliverables=args.deliverables,
        renewal_threshold=args.renewal_threshold,
    )


# ---------------------------------------------------------------------------
# Drive + Sheet integration helpers
# ---------------------------------------------------------------------------

def _drive_filename(data: ContractData) -> str:
    """Match the existing Drive naming convention `YYYYMM - Contrat <Prénom Nom>.pdf`."""
    parts = data.contract_date.split("/")
    if len(parts) == 3:
        yyyymm = f"{parts[2]}{parts[1]}"  # YYYYMM
    else:
        yyyymm = datetime.now().strftime("%Y%m")
    name = f"{data.athlete_first_name} {data.athlete_last_name}".strip()
    return f"{yyyymm} - Contrat {name}.pdf"


def upload_and_link(
    pdf_path: str, data: ContractData, update_sheet: bool
) -> dict:
    """Upload the PDF to Drive and (optionally) write the link in the Sheet.

    Returns the Drive metadata dict (`id`, `name`, `webViewLink`, …) plus
    `sheet_row` and `sheet_cell` if `update_sheet=True` and a row was found.
    """
    from infra.common.google_drive import (
        upload_pdf_to_drive,
        update_sheet_with_contract_link,
    )

    drive_filename = _drive_filename(data)
    print(f"  ↑ Uploading to Drive InfluenceContract as «{drive_filename}»…")
    drive_meta = upload_pdf_to_drive(pdf_path, drive_filename=drive_filename)
    drive_link = drive_meta.get("webViewLink", "")
    print(f"  ✓ Drive link: {drive_link}")

    result = dict(drive_meta)

    if update_sheet:
        print(f"  ↻ Updating Sheet ({data.contract_type})…")
        try:
            row, cell = update_sheet_with_contract_link(
                contract_type=data.contract_type,
                first_name=data.athlete_first_name,
                last_name=data.athlete_last_name,
                drive_link=drive_link,
            )
            if row is not None:
                print(f"  ✓ Sheet updated at {cell} (row {row})")
                result["sheet_row"] = row
                result["sheet_cell"] = cell
            else:
                print(
                    f"  ⚠ Sheet row not found for "
                    f"{data.athlete_first_name} {data.athlete_last_name}. "
                    f"Add the ambassador to the sheet first, then re-run."
                )
        except Exception as e:
            print(f"  ✗ Sheet update failed: {type(e).__name__}: {e}")

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        data, args = parse_args()
        upload_drive = args.upload_drive or args.update_sheet
        update_sheet = args.update_sheet
        dry_run = args.dry_run
    else:
        data = interactive_cli()
        upload_drive = False
        update_sheet = False
        dry_run = False

    path = build_contract(data)
    print(f"\nContrat généré : {path}")

    if dry_run:
        print("(dry-run — Drive upload and Sheet write skipped)")
        return

    if upload_drive:
        upload_and_link(path, data, update_sheet=update_sheet)


if __name__ == "__main__":
    main()

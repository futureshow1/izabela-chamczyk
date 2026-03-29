#!/usr/bin/env python3
"""Generate two instruction PDFs for the Izabela Chamczyk website."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import os

# Try to register a font that supports Polish characters
# reportlab's default fonts handle Latin-2 via UTF-8 encoding
# We'll use Helvetica which has basic Latin support

BASE = Path(__file__).parent

def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontSize=22,
        spaceAfter=6*mm,
        textColor=HexColor('#333333'),
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10*mm,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        'SectionHead',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=8*mm,
        spaceAfter=4*mm,
        textColor=HexColor('#333333'),
        borderWidth=0,
        borderPadding=0,
    ))

    styles.add(ParagraphStyle(
        'SubHead',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=5*mm,
        spaceAfter=3*mm,
        textColor=HexColor('#444444'),
    ))

    styles.add(ParagraphStyle(
        'BodyText2',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3*mm,
        leading=14,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontSize=9,
        leading=13,
        spaceAfter=3*mm,
        backColor=HexColor('#f5f5f5'),
        borderWidth=1,
        borderColor=HexColor('#dddddd'),
        borderPadding=6,
        leftIndent=10,
    ))

    styles.add(ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=2*mm,
        leading=14,
        leftIndent=15,
        bulletIndent=5,
    ))

    styles.add(ParagraphStyle(
        'NoteBox',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        spaceAfter=3*mm,
        backColor=HexColor('#fff3cd'),
        borderWidth=1,
        borderColor=HexColor('#ffc107'),
        borderPadding=8,
        leftIndent=5,
        rightIndent=5,
    ))

    styles.add(ParagraphStyle(
        'StepNumber',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=4*mm,
        spaceAfter=2*mm,
        textColor=HexColor('#2c5aa0'),
        leading=14,
    ))

    styles.add(ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#999999'),
        alignment=TA_CENTER,
    ))

    return styles


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor('#cccccc'),
                       spaceBefore=3*mm, spaceAfter=3*mm)


def note(text, styles):
    return Paragraph(text, styles['NoteBox'])


def code(text, styles):
    return Paragraph(text.replace('\n', '<br/>'), styles['CodeBlock'])


def bullet_list(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles['BulletText']), bulletColor=HexColor('#666666'))
         for item in items],
        bulletType='bullet',
        bulletFontSize=8,
        leftIndent=15,
    )


def step(number, title, styles):
    return Paragraph(f'<b>Krok {number}.</b> {title}', styles['StepNumber'])


def step_en(number, title, styles):
    return Paragraph(f'<b>Step {number}.</b> {title}', styles['StepNumber'])


# ============================================================
# PDF 1: CMS User Guide (for the artist)
# ============================================================

def build_cms_guide():
    filename = str(BASE / "Instrukcja_CMS_Izabela_Chamczyk.pdf")
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Instrukcja CMS - Izabela Chamczyk",
        author="",
    )

    styles = get_styles()
    story = []

    # --- Title page ---
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Instrukcja CMS", styles['DocTitle']))
    story.append(Paragraph("System zarzadzania strona internetowa<br/>izabelachamczyk.com", styles['DocSubtitle']))
    story.append(hr())
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Ten dokument opisuje jak dodawac, edytowac i usuwac prace oraz aktualnosci "
        "na stronie internetowej za pomoca prostego panelu administracyjnego (CMS).",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 5*mm))
    story.append(note(
        "<b>Uwaga:</b> CMS dziala lokalnie na Twoim komputerze. Wszystkie zmiany sa zapisywane "
        "w plikach na dysku. Po dokonaniu zmian nalezy przeslac zaktualizowane pliki na serwer."
    , styles))

    story.append(PageBreak())

    # --- 1. Uruchomienie CMS ---
    story.append(Paragraph("1. Uruchomienie CMS", styles['SectionHead']))

    story.append(step(1, "Otworz <b>Terminal</b> (Finder > Programy > Narzedzia > Terminal)", styles))
    story.append(Paragraph("Lub: nacisnij <b>Cmd + Spacja</b>, wpisz <b>Terminal</b>, nacisnij Enter.", styles['BodyText2']))

    story.append(step(2, "Wpisz komende uruchamiajaca CMS:", styles))
    story.append(code("python3 /sciezka/do/izabela-chamczyk-website/admin.py", styles))
    story.append(Paragraph(
        "Zamiast <i>/sciezka/do/</i> wpisz faktyczna lokalizacje folderu na Twoim komputerze. "
        "Mozesz tez przeciagnac plik <b>admin.py</b> z Findera do okna Terminala - sciezka wpisze sie automatycznie.",
        styles['BodyText2']
    ))

    story.append(step(3, "Otworz przegladarke i wejdz na adres:", styles))
    story.append(code("http://localhost:5000/admin", styles))

    story.append(Paragraph("Zobaczysz panel administracyjny z lista kategorii.", styles['BodyText2']))

    story.append(note(
        "<b>Wskazowka:</b> Aby zakonczyc prace CMS, wroc do Terminala i nacisnij <b>Ctrl + C</b>."
    , styles))

    # --- 2. Panel glowny ---
    story.append(Paragraph("2. Panel glowny (Dashboard)", styles['SectionHead']))
    story.append(Paragraph(
        "Po wejsciu na <b>/admin</b> zobaczysz liste wszystkich 7 kategorii z liczba prac w kazdej:",
        styles['BodyText2']
    ))

    categories = [
        ["Malarstwo", "Obrazy olejne, akrylowe itp."],
        ["Video", "Prace wideo z linkami YouTube/Vimeo"],
        ["Instalacje", "Prace instalacyjne"],
        ["Fotografia", "Prace fotograficzne"],
        ["Performance", "Dokumentacja performance'ow"],
        ["Wojna Dwunastomiesieczna", "Cykl Wojna Dwunastomiesieczna"],
        ["Warsztaty", "Dokumentacja warsztatow"],
    ]

    t = Table(categories, colWidths=[5*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Kliknij nazwe kategorii, aby zobaczyc liste prac.", styles['BodyText2']))

    # --- 3. Dodawanie pracy ---
    story.append(Paragraph("3. Dodawanie nowej pracy", styles['SectionHead']))

    story.append(step(1, 'Wejdz w wybrana kategorie i kliknij przycisk <b>"Dodaj prace"</b>.', styles))
    story.append(step(2, "Wypelnij formularz:", styles))
    story.append(bullet_list([
        "<b>Tytul</b> - nazwa pracy (np. &quot;TOXIC 12&quot;)",
        "<b>Slug</b> - adres URL (wypelnia sie automatycznie, np. &quot;toxic-12&quot;)",
        "<b>Opis</b> - kazda linia to osobny akapit. Pierwsza linia to zwykle technika i wymiary.",
        "<b>Link YouTube/Vimeo</b> - dla prac wideo, wklej pelny adres filmu",
        "<b>Obrazy</b> - wybierz pliki graficzne z dysku (JPG, PNG). Mozna wybrac kilka naraz.",
    ], styles))

    story.append(step(3, 'Kliknij <b>"Zapisz"</b>.', styles))
    story.append(Paragraph("Praca zostanie dodana do listy w wybranej kategorii.", styles['BodyText2']))

    # --- 4. Edytowanie ---
    story.append(Paragraph("4. Edytowanie istniejcej pracy", styles['SectionHead']))
    story.append(bullet_list([
        'Wejdz w kategorie i znajdz prace na liscie.',
        'Kliknij przycisk <b>"Edytuj"</b> obok pracy.',
        'Zmien potrzebne pola - tytul, opis, dodaj nowe obrazy.',
        'Istniejace obrazy sa wyswietlane jako miniaturki. Nowe obrazy zostana dodane do istniejacych.',
        'Kliknij <b>"Zapisz zmiany"</b>.',
    ], styles))

    # --- 5. Usuwanie ---
    story.append(Paragraph("5. Usuwanie pracy", styles['SectionHead']))
    story.append(bullet_list([
        'Kliknij przycisk <b>"Usun"</b> obok pracy na liscie.',
        'Potwierdz usuniecie w oknie dialogowym.',
        'Praca zostanie trwale usunieta z danych.',
    ], styles))
    story.append(note(
        "<b>Uwaga:</b> Usuwanie jest nieodwracalne! Upewnij sie, ze chcesz usunac prace."
    , styles))

    # --- 6. Przebudowa strony ---
    story.append(Paragraph("6. Przebudowa strony", styles['SectionHead']))
    story.append(Paragraph(
        "Po dodaniu, edycji lub usunieciu prac, strona HTML musi zostac odswiezona. "
        "W tym celu:",
        styles['BodyText2']
    ))
    story.append(step(1, 'Kliknij przycisk <b>"Przebuduj strone"</b> na gorze panelu.', styles))
    story.append(step(2, "Poczekaj kilka sekund az skrypt przetworzy dane.", styles))
    story.append(step(3, 'Zobaczysz komunikat <b>"Strona zostala przebudowana"</b>.', styles))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Po przebudowie mozesz sprawdzic strone lokalnie wchodzac na "
        "<b>http://localhost:5000</b> (bez /admin).",
        styles['BodyText2']
    ))

    # --- 7. Publikacja ---
    story.append(Paragraph("7. Publikacja zmian na serwer", styles['SectionHead']))
    story.append(Paragraph(
        "Po przebudowie strony, zaktualizowane pliki sa gotowe do przeslania na serwer. "
        "Nalezy przeslac caly folder strony na serwer hostingowy:",
        styles['BodyText2']
    ))
    story.append(bullet_list([
        "Uzyj programu <b>FileZilla</b> (darmowy) lub <b>Cyberduck</b> do przeslania plikow przez FTP/SFTP.",
        "Polacz sie z serwerem uzywajac danych logowania od hostingu.",
        "Przeslij zawartosc folderu <b>izabela-chamczyk-website</b> do katalogu glownego strony na serwerze (zwykle <b>public_html</b> lub <b>www</b>).",
        "Nie przesylaj plikow: <b>admin.py</b>, <b>build_site.py</b>, <b>generate_pdfs.py</b>, plikow <b>*.json</b> - te pliki sa potrzebne tylko lokalnie.",
    ], styles))

    story.append(note(
        "<b>Wskazowka:</b> Wystarczy przeslac tylko zmienione pliki. "
        "Jesli dodano nowa prace w kategorii Malarstwo, przeslij folder <b>prace/malarstwo/</b>, "
        "plik <b>malarstwo.html</b>, oraz nowe obrazy z <b>images/works/</b>."
    , styles))

    # --- 8. Struktura plikow ---
    story.append(PageBreak())
    story.append(Paragraph("8. Podsumowanie - schemat pracy", styles['SectionHead']))

    workflow = [
        ["1.", "Uruchom CMS", "python3 admin.py"],
        ["2.", "Otworz panel", "http://localhost:5000/admin"],
        ["3.", "Dodaj / edytuj / usun prace", "Przez formularz w przegladarce"],
        ["4.", "Przebuduj strone", 'Przycisk "Przebuduj strone"'],
        ["5.", "Sprawdz efekt", "http://localhost:5000"],
        ["6.", "Przeslij na serwer", "FTP/SFTP (FileZilla / Cyberduck)"],
        ["7.", "Zamknij CMS", "Ctrl + C w Terminalu"],
    ]

    t = Table(workflow, colWidths=[1*cm, 4*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#ffffff')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ]))
    story.append(t)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "W razie problemow technicznych skontaktuj sie z osoba, ktora przygotowala strone.",
        styles['BodyText2']
    ))

    doc.build(story)
    print(f"Created: {filename}")


# ============================================================
# PDF 2: Deployment / Installation Guide
# ============================================================

def build_deployment_guide():
    filename = str(BASE / "Instrukcja_Instalacji_Strony.pdf")
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Instrukcja instalacji strony - Izabela Chamczyk",
        author="",
    )

    styles = get_styles()
    story = []

    # --- Title page ---
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Instrukcja instalacji strony<br/>i systemu CMS", styles['DocTitle']))
    story.append(Paragraph("izabelachamczyk.com", styles['DocSubtitle']))
    story.append(hr())
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Ten dokument opisuje krok po kroku jak zainstalowac strone internetowa "
        "i system CMS na komputerze, oraz jak opublikowac strone w internecie. "
        "Instrukcja jest przeznaczona dla osob nietechnicznych.",
        styles['BodyText2']
    ))

    story.append(PageBreak())

    # --- Table of contents ---
    story.append(Paragraph("Spis tresci", styles['SectionHead']))
    toc = [
        "1. Co jest w paczce plikow",
        "2. Wymagania systemowe",
        "3. Instalacja na komputerze (Mac)",
        "4. Instalacja na komputerze (Windows)",
        "5. Uruchomienie strony lokalnie",
        "6. Uruchomienie CMS",
        "7. Publikacja strony w internecie",
        "8. Aktualizacja strony po zmianach",
        "9. Rozwiazywanie problemow",
    ]
    for item in toc:
        story.append(Paragraph(item, styles['BodyText2']))

    story.append(PageBreak())

    # --- 1. Zawartosc paczki ---
    story.append(Paragraph("1. Co jest w paczce plikow", styles['SectionHead']))
    story.append(Paragraph("Folder <b>izabela-chamczyk-website</b> zawiera:", styles['BodyText2']))

    files_table = [
        ["Plik / folder", "Opis"],
        ["index.html, prace.html, ...", "Strony HTML (gotowe do publikacji)"],
        ["css/style.css", "Arkusz stylow strony"],
        ["js/main.js", "Skrypt JavaScript (slider, menu)"],
        ["images/", "Wszystkie obrazy strony (~90 MB)"],
        ["en/", "Wersja angielska strony"],
        ["prace/, akcje/", "Podstrony galerii"],
        ["admin.py", "System CMS (panel administracyjny)"],
        ["build_site.py", "Skrypt budujacy strone z danych"],
        ["chamczyk_paintings_data.json", "Dane malarstwa (86 prac)"],
        ["chamczyk_works_data.json", "Dane pozostalych kategorii (76 prac)"],
    ]

    t = Table(files_table, colWidths=[5.5*cm, 8.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)

    story.append(Spacer(1, 3*mm))
    story.append(note(
        "<b>Wazne:</b> Nie zmieniaj nazw plikow ani struktury folderow. "
        "Strona i CMS zaleza od tej dokladnej struktury."
    , styles))

    # --- 2. Wymagania ---
    story.append(Paragraph("2. Wymagania systemowe", styles['SectionHead']))
    story.append(Paragraph("Do uruchomienia CMS potrzebujesz:", styles['BodyText2']))
    story.append(bullet_list([
        "<b>Python 3.10 lub nowszy</b> - jezyk programowania (darmowy)",
        "<b>Przegladarka internetowa</b> - Chrome, Safari, Firefox",
        "<b>~200 MB wolnego miejsca</b> na dysku",
        "<b>Program FTP</b> do przesylania na serwer (np. FileZilla, Cyberduck)",
    ], styles))

    story.append(Paragraph("Do samej publikacji strony (bez CMS) nie potrzebujesz Pythona.", styles['BodyText2']))

    # --- 3. Mac ---
    story.append(Paragraph("3. Instalacja na komputerze (Mac)", styles['SectionHead']))

    story.append(Paragraph("<b>Sprawdzenie Pythona</b>", styles['SubHead']))
    story.append(Paragraph("Mac zwykle ma juz zainstalowanego Pythona. Sprawdz:", styles['BodyText2']))
    story.append(step(1, "Otworz <b>Terminal</b> (Cmd + Spacja, wpisz Terminal, Enter)", styles))
    story.append(step(2, "Wpisz:", styles))
    story.append(code("python3 --version", styles))
    story.append(Paragraph(
        'Jesli zobaczysz np. <b>"Python 3.12.0"</b> lub wyzsza - Python jest zainstalowany.',
        styles['BodyText2']
    ))
    story.append(Paragraph(
        'Jesli zobaczysz blad - zainstaluj Pythona:',
        styles['BodyText2']
    ))
    story.append(step(3, "Wejdz na <b>python.org/downloads</b> w przegladarce", styles))
    story.append(step(4, 'Kliknij zolty przycisk <b>"Download Python 3.x.x"</b>', styles))
    story.append(step(5, "Otworz pobrany plik i postepuj zgodnie z instrukcjami instalatora", styles))

    story.append(Paragraph("<b>Skopiowanie plikow strony</b>", styles['SubHead']))
    story.append(step(1, "Skopiuj caly folder <b>izabela-chamczyk-website</b> w wybrane miejsce na dysku", styles))
    story.append(Paragraph(
        "Np. do folderu <b>Dokumenty</b> lub na <b>Pulpit</b>. Zapamietaj gdzie go umiescilas.",
        styles['BodyText2']
    ))

    # --- 4. Windows ---
    story.append(Paragraph("4. Instalacja na komputerze (Windows)", styles['SectionHead']))

    story.append(Paragraph("<b>Instalacja Pythona</b>", styles['SubHead']))
    story.append(step(1, "Wejdz na <b>python.org/downloads</b> w przegladarce", styles))
    story.append(step(2, 'Kliknij <b>"Download Python 3.x.x"</b>', styles))
    story.append(step(3, "Otworz pobrany plik instalacyjny", styles))
    story.append(note(
        '<b>WAZNE:</b> Na pierwszym ekranie instalatora zaznacz checkbox '
        '<b>"Add Python to PATH"</b> (na dole ekranu). To jest kluczowe!'
    , styles))
    story.append(step(4, 'Kliknij <b>"Install Now"</b> i poczekaj', styles))

    story.append(Paragraph("<b>Sprawdzenie instalacji</b>", styles['SubHead']))
    story.append(step(1, "Otworz <b>Wiersz polecen</b> (nacisnij Win + R, wpisz <b>cmd</b>, Enter)", styles))
    story.append(step(2, "Wpisz:", styles))
    story.append(code("python --version", styles))
    story.append(Paragraph(
        'Jesli zobaczysz wersje Pythona - instalacja przebiegla pomyslnie.',
        styles['BodyText2']
    ))
    story.append(note(
        "<b>Uwaga Windows:</b> Na Windowsie komenda to <b>python</b> (nie python3). "
        "W dalszej czesci instrukcji zamien <b>python3</b> na <b>python</b>."
    , styles))

    story.append(Paragraph("<b>Skopiowanie plikow</b>", styles['SubHead']))
    story.append(Paragraph(
        "Skopiuj caly folder <b>izabela-chamczyk-website</b> w wybrane miejsce, "
        "np. do <b>Dokumenty</b> lub na <b>Pulpit</b>.",
        styles['BodyText2']
    ))

    # --- 5. Uruchomienie lokalne ---
    story.append(PageBreak())
    story.append(Paragraph("5. Uruchomienie strony lokalnie (podglad)", styles['SectionHead']))
    story.append(Paragraph(
        "Mozesz przegladac strone lokalnie bez przesylania na serwer:",
        styles['BodyText2']
    ))

    story.append(Paragraph("<b>Sposob 1: Przez CMS (zalecany)</b>", styles['SubHead']))
    story.append(Paragraph(
        "Uruchom CMS (patrz punkt 6) - strona bedzie dostepna pod <b>http://localhost:5000</b>",
        styles['BodyText2']
    ))

    story.append(Paragraph("<b>Sposob 2: Prosty serwer</b>", styles['SubHead']))
    story.append(code(
        "cd /sciezka/do/izabela-chamczyk-website\n"
        "python3 -m http.server 8080",
        styles
    ))
    story.append(Paragraph("Otworz przegladarke: <b>http://localhost:8080</b>", styles['BodyText2']))

    story.append(Paragraph("<b>Sposob 3: Bezposrednio</b>", styles['SubHead']))
    story.append(Paragraph(
        "Mozesz tez po prostu otworzyc plik <b>index.html</b> w przegladarce (dwuklik). "
        "Niektore elementy moga nie dzialac idealnie w tym trybie.",
        styles['BodyText2']
    ))

    # --- 6. CMS ---
    story.append(Paragraph("6. Uruchomienie CMS", styles['SectionHead']))

    story.append(Paragraph("<b>Mac:</b>", styles['SubHead']))
    story.append(step(1, "Otworz Terminal", styles))
    story.append(step(2, "Wpisz (lub przeciagnij plik admin.py do Terminala):", styles))
    story.append(code("python3 /Users/TwojaNazwa/Documents/izabela-chamczyk-website/admin.py", styles))
    story.append(step(3, "Otworz przegladarke: <b>http://localhost:5000/admin</b>", styles))

    story.append(Paragraph("<b>Windows:</b>", styles['SubHead']))
    story.append(step(1, "Otworz Wiersz polecen (Win + R > cmd > Enter)", styles))
    story.append(step(2, "Wpisz:", styles))
    story.append(code('python "C:\\Users\\TwojaNazwa\\Documents\\izabela-chamczyk-website\\admin.py"', styles))
    story.append(step(3, "Otworz przegladarke: <b>http://localhost:5000/admin</b>", styles))

    story.append(note(
        "<b>Wskazowka:</b> Mozesz tez dwukliknac plik <b>admin.py</b> jesli Python jest "
        "prawidlowo zainstalowany. Otworzy sie okno terminala z dzialajacym serwerem."
    , styles))

    story.append(Paragraph(
        'Aby zakonczyc prace CMS: wroc do Terminala/Wiersza polecen i nacisnij <b>Ctrl + C</b>.',
        styles['BodyText2']
    ))

    # --- 7. Publikacja ---
    story.append(PageBreak())
    story.append(Paragraph("7. Publikacja strony w internecie", styles['SectionHead']))

    story.append(Paragraph("<b>Czego potrzebujesz:</b>", styles['SubHead']))
    story.append(bullet_list([
        "<b>Hosting</b> - usluga przechowywania strony w internecie (np. home.pl, OVH, nazwa.pl, LH.pl). Wystarczy najtanszy pakiet z obsluga plikow statycznych.",
        "<b>Domena</b> - adres strony (np. izabelachamczyk.com). Mozna kupic przy zakupie hostingu.",
        "<b>Dane FTP</b> - login, haslo i adres serwera. Dostaniesz je od hostingu po zakupie.",
        "<b>Program FTP</b> - FileZilla (darmowy, pobierz z filezilla-project.org) lub Cyberduck.",
    ], styles))

    story.append(Paragraph("<b>Przesylanie plikow (FileZilla):</b>", styles['SubHead']))
    story.append(step(1, "Zainstaluj i otworz FileZilla", styles))
    story.append(step(2, "Na gorze wpisz dane z hostingu:", styles))

    ftp_table = [
        ["Host:", "np. ftp.izabelachamczyk.com"],
        ["Uzytkownik:", "login z hostingu"],
        ["Haslo:", "haslo z hostingu"],
        ["Port:", "21 (lub zostaw puste)"],
    ]
    t = Table(ftp_table, colWidths=[3.5*cm, 10.5*cm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
    ]))
    story.append(t)

    story.append(step(3, 'Kliknij <b>"Polacz"</b>', styles))
    story.append(step(4, "Po lewej stronie: znajdz folder <b>izabela-chamczyk-website</b> na swoim komputerze", styles))
    story.append(step(5, "Po prawej stronie: wejdz do folderu <b>public_html</b> (lub <b>www</b>) na serwerze", styles))
    story.append(step(6, "Zaznacz WSZYSTKIE pliki i foldery po lewej (Ctrl+A / Cmd+A)", styles))

    story.append(note(
        "<b>WAZNE:</b> NIE przesylaj plikow: <b>admin.py</b>, <b>build_site.py</b>, <b>generate_pdfs.py</b>, "
        "plikow <b>*.json</b> i plikow <b>*.pdf</b>. Te pliki sa potrzebne tylko na Twoim komputerze, "
        "nie powinny byc publicznie dostepne na serwerze."
    , styles))

    story.append(step(7, "Przeciagnij zaznaczone pliki na prawa strone (na serwer)", styles))
    story.append(step(8, "Poczekaj az wszystkie pliki sie przesla (moze potrwac kilka minut)", styles))
    story.append(step(9, "Otworz adres strony w przegladarce i sprawdz czy dziala", styles))

    # Files to exclude
    story.append(Paragraph("<b>Pliki do przeslania vs. pliki lokalne:</b>", styles['SubHead']))

    upload_table = [
        ["Przeslij na serwer", "Zostaw lokalnie (NIE przesylaj)"],
        ["index.html", "admin.py"],
        ["prace.html, akcje.html, ...", "build_site.py"],
        ["css/", "generate_pdfs.py"],
        ["js/", "chamczyk_paintings_data.json"],
        ["images/", "chamczyk_works_data.json"],
        ["en/", "*.pdf (instrukcje)"],
        ["prace/, akcje/", ""],
    ]

    t = Table(upload_table, colWidths=[7*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('BACKGROUND', (0, 1), (0, -1), HexColor('#e8f5e9')),
        ('BACKGROUND', (1, 1), (1, -1), HexColor('#ffebee')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)

    # --- 8. Aktualizacja ---
    story.append(PageBreak())
    story.append(Paragraph("8. Aktualizacja strony po zmianach", styles['SectionHead']))
    story.append(Paragraph("Pelny proces aktualizacji strony:", styles['BodyText2']))

    workflow = [
        ["1.", "Uruchom CMS", "python3 admin.py", "Terminal / Wiersz polecen"],
        ["2.", "Otworz panel", "localhost:5000/admin", "Przegladarka"],
        ["3.", "Dokonaj zmian", "Dodaj/edytuj/usun prace", "Panel CMS"],
        ["4.", "Przebuduj strone", 'Przycisk "Przebuduj"', "Panel CMS"],
        ["5.", "Sprawdz efekt", "localhost:5000", "Przegladarka"],
        ["6.", "Zamknij CMS", "Ctrl + C", "Terminal"],
        ["7.", "Otworz FileZilla", "Polacz z serwerem", "FileZilla"],
        ["8.", "Przeslij zmienione pliki", "Na serwer", "FileZilla"],
        ["9.", "Sprawdz strone", "izabelachamczyk.com", "Przegladarka"],
    ]

    t = Table(
        [["Nr", "Co", "Jak", "Gdzie"]] + workflow,
        colWidths=[1*cm, 3.5*cm, 4.5*cm, 4.5*cm]
    )
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8f8f8')]),
    ]))
    story.append(t)

    story.append(Spacer(1, 5*mm))
    story.append(note(
        "<b>Wskazowka:</b> Nie musisz przesylac wszystkich plikow za kazdym razem. "
        "Jesli np. dodajesz nowa prace w kategorii Malarstwo, wystarczy przeslac:<br/>"
        "- folder <b>prace/malarstwo/</b> (nowa podstrona)<br/>"
        "- plik <b>malarstwo.html</b> (zaktualizowana galeria)<br/>"
        "- nowe obrazy z <b>images/works/</b><br/>"
        "- plik <b>images/thumbs/</b> (jesli zmienila sie miniaturka)"
    , styles))

    # --- 9. Rozwiazywanie problemow ---
    story.append(Paragraph("9. Rozwiazywanie problemow", styles['SectionHead']))

    problems = [
        ['"python3 nie jest rozpoznawane..."',
         "Python nie jest zainstalowany lub nie jest dodany do PATH. "
         "Zainstaluj ponownie i zaznacz 'Add to PATH'. Na Windows uzyj 'python' zamiast 'python3'."],
        ['"Port 5000 jest juz uzywany"',
         "Inny program uzywa portu 5000. Zamknij go lub zmien port w admin.py "
         "(linia z numerem 5000 na np. 5001)."],
        ['"Strona nie wyswietla obrazow"',
         "Sprawdz czy folder images/ zostal przeslany na serwer. "
         "Sprawdz czy obrazy sa w podfolderach works/, thumbs/, news/."],
        ['"Przebudowa nie dziala"',
         "Upewnij sie, ze pliki .json sa w folderze strony. "
         "Sprawdz czy oba pliki JSON sa obok admin.py."],
        ['"Strona wyglada zle na telefonie"',
         "Strona jest responsywna i powinna dzialac. Wyczysc cache przegladarki (Ctrl+Shift+R). "
         "Sprawdz czy plik css/style.css zostal przeslany."],
        ['"Nie moge sie polaczyc przez FTP"',
         "Sprawdz dane logowania od hostingu (host, login, haslo). "
         "Upewnij sie ze wpisujesz adres FTP, nie adres strony."],
    ]

    for problem, solution in problems:
        story.append(Paragraph(f'<b>Problem:</b> {problem}', styles['BodyText2']))
        story.append(Paragraph(f'<b>Rozwiazanie:</b> {solution}', styles['BodyText2']))
        story.append(Spacer(1, 2*mm))

    story.append(hr())
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "W razie problemow technicznych skontaktuj sie z osoba, ktora przygotowala strone.",
        styles['BodyText2']
    ))

    doc.build(story)
    print(f"Created: {filename}")


if __name__ == "__main__":
    build_cms_guide()
    build_deployment_guide()
    print("Done! Both PDFs generated.")

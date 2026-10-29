import os, sys, json, time, requests, re
import config

RELATIONSHIP_CURRICULUM = [['Sekrety więzi emocjonalnej', 'Zrozumieć style przywiązania i głębokie lęki, by kochać w poczuciu bezpieczeństwa'], ['Sztuka mówienia bez ranienia', 'Wyrażać potrzeby z czułością i jasnością, bez wyrzutów i obrony'], ['Nauka stawiania zdrowych granic', 'Mówić nie z życzliwością, by chronić harmonię związku i poczucie własnej wartości'], ['Uzdrowienie lęku przed odrzuceniem i porzuceniem', 'Odzyskać wewnętrzne bezpieczeństwo i zbudować niezachwiane zaufanie w więzi'], ['5 języków miłości na co dzień', 'Odszyfrować głębokie potrzeby emocjonalne partnera i karmić miłość każdego dnia'], ['Wrażliwość: niewidzialna siła związku', 'Dlaczego odwaga bycia autentycznym i niedoskonałym to jedyny prawdziwy klucz do intymności'], ['Rozbrajanie konfliktów bez urazy', 'Zamieniać nieporozumienia w szanse na zbliżenie i wzajemne zrozumienie'], ['Wyjście z zależności emocjonalnej', 'Jak pielęgnować emocjonalną niezależność i w pełni rozkwitać we dwoje'], ['Aktywne słuchanie i moc ciszy', 'Usłyszeć to, co serce drugiej osoby szepcze zza zmęczenia i codziennych słów'], ['Odbudowa zaufania po zranieniu', 'Cierpliwa droga naprawy, prawdy i wspólnego przebaczenia']]

DEFAULT_5_ACTS = [['Akt 1: Rozpoznanie serca', 'Ciepłe wprowadzenie i zanurzenie w rzeczywistość wyzwania relacyjnego'], ['Akt 2: Nieświadome korzenie', 'Psychologiczna eksploracja lęków, ran z dzieciństwa i naszych odruchów obronnych'], ['Akt 3: Praktyczne klucze i kojące słowa', 'Przemieniające zdania, życzliwe postawy i konstruktywne codzienne dialogi'], ['Akt 4: Przechodzenie przez emocjonalne burze', 'Radzenie sobie ze złością i wycofaniem oraz pokonywanie napięć bez paniki'], ['Akt 5: Ćwiczenie serca i codzienne błogosławieństwo', 'Życzliwe wyzwanie introspekcyjne, rytuał więzi na tydzień i przesłanie nadziei']]

def load_history_topics() -> list:
    """Reads all past published topics from published_videos.json and history.json to ensure no repeats."""
    past = []
    for fname in ["published_videos.json", "history.json"]:
        fpath = os.path.join(config.BASE_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("topic"):
                                t = item["topic"].strip()
                                if t not in past:
                                    past.append(t)
            except Exception:
                pass
    return past

def generate_dynamic_topic_ai(past_topics: list, ep_num: int = 1) -> dict:
    """Pyta Pollinations AI z historią poprzednich tematów o zupełnie nowy, niepowtarzający się polski temat o relacjach."""
    key = config.POLLINATIONS_API_KEY
    if not key:
        return None

    past_sample = past_topics[-30:] if len(past_topics) > 30 else past_topics
    prompt = (
        f"Jesteś producentką wykonawczą i pomysłodawczynią polskiego podcastu '{config.CHANNEL_NAME}'.\n"
        f"Slogan: {config.TAGLINE}\n"
        f"Format: Intymny solowy podcast z {config.HOST1_NAME}, życzliwą psycholożką i powierniczką.\n"
        f"Tematyka: Ludzkie relacje, psychologia miłości, więź, komunikacja, czułość, odporność związku.\n"
        f"Zasada językowa: WSZYSTKO musi być napisane elegancką, naturalną i ciepłą polszczyzną.\n\n"
        f"Już omówione odcinki (NIE POWTARZAĆ):\n"
        + json.dumps(past_sample, indent=2, ensure_ascii=False) + "\n\n"
        f"Wygeneruj JEDEN NOWY, urzekający i wzbogacający temat odcinka #{ep_num}.\n\n"
        f"FORMAT WYJŚCIA: Zwróć WYŁĄCZNIE poprawny obiekt JSON (bez markdowna, bez wstępu):\n"
        "{\n"
        f'  "id": "ep_{ep_num}",\n'
        '  "topic": "Urzekający polski tytuł (np.: Nauczyć się wybaczać nie zapominając o sobie)",\n'
        '  "focus": "Jedno zdanie: Co słuchacz zrozumie i przemieni w swoich więziach",\n'
        '  "thumbnail_title_1": "PIERWSZE SŁOWA (MAX. 16 ZNAKÓW)",\n'
        '  "thumbnail_title_2": "DRUGIE SŁOWA (MAX. 16 ZNAKÓW)",\n'
        '  "thumbnail_hook": "Chwytliwy haczyk (np.: Ocalić związek z łagodnością)",\n'
        '  "acts": [\n'
        '    ["Akt 1: Tytuł", "Opis fokusu aktu..."],\n'
        '    ["Akt 2: Tytuł", "Opis fokusu aktu..."],\n'
        '    ["Akt 3: Tytuł", "Opis fokusu aktu..."],\n'
        '    ["Akt 4: Tytuł", "Opis fokusu aktu..."],\n'
        '    ["Akt 5: Tytuł", "Opis fokusu aktu..."]\n'
        '  ]\n'
        "}" 
    )

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": config.POLLINATIONS_MODEL,
        "messages": [
            {"role": "system", "content": "Jesteś najwyższej klasy producentem podcastów. Odpowiadasz wyłącznie poprawnym JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.82
    }

    for attempt in range(3):
        try:
            print(f"[StoryGenerator] Synteza AI nowego tematu relacyjnego (próba {attempt+1}/3)...")
            resp = requests.post(config.POLLINATIONS_ENDPOINT, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"].strip()
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:].strip()
                    raw = raw.split("```")[0].strip()
                data = json.loads(raw)
                topic_val = data.get("topic", "")
                if topic_val and data.get("acts") and len(data["acts"]) >= 4:
                    t_lower = topic_val.lower().strip()
                    past_lowers = [p.lower().strip() for p in past_topics]
                    if t_lower not in past_lowers:
                        print(f"[StoryGenerator] Pomyślnie wygenerowano nowy temat: '{topic_val}'")
                        return data
        except Exception as e:
            print(f"[StoryGenerator] Błąd próby tematu AI ({attempt+1}) : {e}")
            time.sleep(1.5)
    return None

def get_next_topic(history: list, custom_topic: str = None, ep_num: int = 1) -> dict:
    if custom_topic:
        words = custom_topic.split()
        mid = len(words) // 2
        t1 = " ".join(words[:mid]) if mid > 0 else words[0]
        t2 = " ".join(words[mid:]) if mid > 0 else "RELACJE"
        return {
            "id": f"custom_{ep_num}",
            "topic": custom_topic,
            "focus": "Intymna i kojąca refleksja o dynamice ludzkich relacji",
            "thumbnail_title_1": t1[:16].upper(),
            "thumbnail_title_2": t2[:16].upper(),
            "thumbnail_hook": "Zrozumieć serce",
            "acts": DEFAULT_5_ACTS
        }

    past_topics = load_history_topics()

    # 1. AI Dynamic Generation
    ai_topic = generate_dynamic_topic_ai(past_topics, ep_num=ep_num)
    if ai_topic:
        t1 = ai_topic.get("thumbnail_title_1", "")
        t2 = ai_topic.get("thumbnail_title_2", "")
        if not t1 or not t2:
            words = ai_topic["topic"].split()
            mid = len(words) // 2
            t1 = " ".join(words[:mid])
            t2 = " ".join(words[mid:])
        return {
            "id": ai_topic.get("id", f"ep_{ep_num}"),
            "topic": ai_topic["topic"],
            "focus": ai_topic.get("focus", "Zrozumieć i pielęgnować nasze relacje emocjonalne"),
            "thumbnail_title_1": t1[:16].upper(),
            "thumbnail_title_2": t2[:16].upper(),
            "thumbnail_hook": ai_topic.get("thumbnail_hook", "Psychologia pary"),
            "acts": ai_topic.get("acts", DEFAULT_5_ACTS)
        }

    # 2. Curated Curriculum Fallback
    past_lowers = [p.lower().strip() for p in past_topics]
    for idx, (title, focus) in enumerate(RELATIONSHIP_CURRICULUM):
        if title.lower().strip() not in past_lowers:
            print(f"[StoryGenerator] Wybrano temat z katalogu: '{title}'")
            words = title.split()
            mid = len(words) // 2
            t1 = " ".join(words[:mid])
            t2 = " ".join(words[mid:])
            return {
                "id": f"ep_{ep_num}",
                "topic": title,
                "focus": focus,
                "thumbnail_title_1": t1[:16].upper(),
                "thumbnail_title_2": t2[:16].upper(),
                "thumbnail_hook": "Sztuka ludzkiej więzi",
                "acts": DEFAULT_5_ACTS
            }

    # 3. Endless Cycle Variation
    cycle = (ep_num - 1) // len(RELATIONSHIP_CURRICULUM) + 1
    cat_idx = (ep_num - 1) % len(RELATIONSHIP_CURRICULUM)
    base_title, base_focus = RELATIONSHIP_CURRICULUM[cat_idx]
    title = f"{base_title} : Pogłębienie i uzdrowienie (część {cycle})"
    words = title.split()
    mid = len(words) // 2
    t1 = " ".join(words[:mid])
    t2 = " ".join(words[mid:])
    return {
        "id": f"ep_{ep_num}",
        "topic": title,
        "focus": f"Kluczowe pogłębienie: {base_focus}",
        "thumbnail_title_1": t1[:16].upper(),
        "thumbnail_title_2": t2[:16].upper(),
        "thumbnail_hook": f"Podejście terapeutyczne #{cycle}",
        "acts": DEFAULT_5_ACTS
    }

def generate_curated_fallback_act(act_idx: int, act_title: str, topic: str, target_turns: int = 40) -> list:
    """Polskie monologi relacyjne pisane z terapeutycznym ciepłem i poetycką elegancją."""
    h1 = config.HOST1_NAME
    s1 = config.HOST1_SPEAKER
    cname = config.CHANNEL_NAME

    solo_act_scripts = [
        # Akt 1: Rozpoznanie serca
        [
        f"Witaj w {cname}. Bardzo się cieszę, że jesteś dziś ze mną w tej intymnej chwili.",
        f"Dziś zatrzymamy się na chwilę przy temacie niezwykle ważnym: {topic}.",
        f"W zgiełku codzienności często zapominamy wsłuchać się w bicie własnego serca.",
        f"Ludzkie relacje są jednocześnie naszym największym schronieniem i najuczciwszym lustrem.",
        f"Kiedy kochamy, odsłaniamy najgłębsze pragnienia, ale też kruchość.",
        f"Może znasz to ciche nieporozumienie, które czasem wkrada się między dwoje ludzi.",
        f"Dwoje ludzi, którzy głęboko się kochają, a przestają się rozumieć.",
        f"Weź ze mną głęboki oddech i odłóż całe nagromadzone napięcie.",
        f"Ten podcast to twoje sanktuarium, miejsce, gdzie wrażliwość staje się wielką siłą.",
        f"Nie szukamy tu doskonałości ani nie rozdajemy wyrzutów.",
        ],
        # Akt 2: Nieświadome korzenie
        [
        f"Aby zrozumieć to, co dzieje się w naszych dzisiejszych relacjach, często trzeba spojrzeć wstecz.",
        f"Nasz sposób kochania i przywiązywania się ma korzenie w najwcześniejszych doświadczeniach dzieciństwa.",
        f"To pierwsze więzi rodzinne ukształtowały nasz emocjonalny kompas.",
        f"Gdy zabrakło poczucia bezpieczeństwa, może rodzić się paniczny lęk przed porzuceniem.",
        f"Te nieświadome odruchy to nasze style przywiązania, nasze ochronne zbroje.",
        f"Kiedy partner oddala się, by odetchnąć, nasze wewnętrzne dziecko wpada w panikę.",
        f"Wydaje nam się, że miłość znika, a to jedynie potrzeba przestrzeni.",
        f"To zrozumienie zmienia absolutnie wszystko w dynamice związku.",
        f"Złość to często rozpaczliwe wołanie o to, by zostać dostrzeżonym i ukojonym.",
        f"Gdy za maską obojętności dostrzeżemy kruchość, czułość odradza się sama.",
        ],
        # Akt 3: Praktyczne klucze i kojące słowa
        [
        f"Przejdźmy teraz do codziennej praktyki tej komunikacji serca.",
        f"Największa pułapka rozmowy: atakować tożsamość drugiej osoby zamiast wyrażać własne odczucia.",
        f"Zamień 'Nigdy mnie nie słuchasz' na proste 'Czuję się teraz samotnie'.",
        f"Zobacz, jak ten drobny niuans natychmiast rozbraja potrzebę kontrataku.",
        f"Kto mówi o sobie, szczerze i wrażliwie, zaprasza drugą osobę do ukojenia.",
        f"Kto oskarża, zmusza drugą osobę do przywdziania zbroi.",
        f"Kolejny cudowny sekret kryje się w sztuce małych, niespodziewanych gestów.",
        f"Te drobne gesty wysyłają do układu nerwowego mocny sygnał: ze mną jesteś bezpieczny.",
        f"Nie czekaj na wielkie rocznice, by świętować obecność kochanej osoby.",
        f"Powiedz dziś po prostu 'Rozumiem cię i jestem przy tobie', to ma nieskończoną moc uzdrawiania.",
        ],
        # Akt 4: Przechodzenie przez emocjonalne burze
        [
        f"Nawet przy największej mądrości burze i tarcia są częścią życia we dwoje.",
        f"Dwoje ludzi dzielących codzienność nieuchronnie przeżywa chwile niezgody i zmęczenia.",
        f"Sekret trwałych par nie tkwi w braku konfliktów, lecz w sposobie ich przechodzenia.",
        f"Gdy napięcie rośnie, a ton się zaostrza, nasz mózg przechodzi w tryb przetrwania.",
        f"W tym stanie alarmu żadna konstruktywna rozmowa nie może się udać.",
        f"Najodważniejszy krok to kojąca pauza: 'Kocham cię, weźmy dziesięć minut na oddech'.",
        f"Taki oddech pozwala sercu zwolnić i oszczędza raniących słów, których potem żałujemy.",
        f"Duma i ego to najgorsi doradcy, gdy chodzi o miłość.",
        f"Zapytaj siebie: wolisz mieć za wszelką cenę rację, czy być w pokoju i więzi?",
        f"Przyznanie się do własnych błędów to nigdy słabość, to szczyt elegancji serca.",
        ],
        # Akt 5: Ćwiczenie serca i codzienne błogosławieństwo
        [
        f"Dotarliśmy do końca naszej wspólnej refleksji na tym kanale.",
        f"Aby zakorzenić to zrozumienie w życiu, mam dla ciebie wyzwanie serca na ten tydzień.",
        f"Dziś lub jutro powiedz bliskiej osobie, jakie piękno wnosi w twoje życie jej obecność.",
        f"Nie mów o tym, co robi, lecz o tym, kim dla ciebie jest i jakie światło roztacza.",
        f"Zobaczysz, jak szczere słowo potrafi rozjaśnić twarz i ogrzać cały dzień.",
        f"Pamiętaj, że zasługujesz na miłość pełną szacunku, łagodności i uważności.",
        f"Dziękuję ci z całego serca za słuchanie i wierność na {cname}.",
        f"Zasubskrybuj, aby nie przegapić żadnego z naszych łagodnych i rozjaśniających spotkań.",
        f"Dbaj o siebie i bliskich, i pielęgnuj zawsze cenną sztukę więzi.",
        f"Do zobaczenia wkrótce w nowym odcinku pełnym czułości i jasności.",
        ],
    ]

    safe_act_idx = min(act_idx, len(solo_act_scripts) - 1)
    lines = solo_act_scripts[safe_act_idx]
    result = []
    for l in lines:
        result.append({"speaker": s1, "name": h1, "text": l})
        if len(result) >= target_turns:
            break

    while len(result) < target_turns:
        for l in lines:
            prefix = "Zastanawiając się nad tym z sercem, "
            result.append({"speaker": s1, "name": h1, "text": f"{prefix}{l[0].lower() + l[1:] if len(l) > 1 else l}"})
            if len(result) >= target_turns:
                break

    return result

def generate_act_ai(act_idx: int, act_title: str, topic_title: str, focus: str, target_turns: int = 35) -> list:
    key = config.POLLINATIONS_API_KEY
    if not key:
        return None

    if act_idx == 0:
        transition_note = "Akt otwarcia: Przywitaj ciepło słuchacza na kanale, stwórz łagodną, intymną atmosferę i wrażliwie wprowadź w temat."
    elif act_idx == 1:
        transition_note = "Akt 2: WAŻNE - NIE mów 'witaj' ani 'witaj ponownie'. Przejdź bezpośrednio i naturalnie do korzeni psychologicznych i nieświadomości."
    elif act_idx == 2:
        transition_note = "Akt 3: WAŻNE - NIE mów 'witaj'. Przejdź płynnie do konkretnych przykładów z codzienności, łagodnej komunikacji i kojących słów."
    elif act_idx == 3:
        transition_note = "Akt 4: WAŻNE - NIE mów 'witaj'. Kontynuuj o zarządzaniu kryzysami, kłótniach i gojeniu ran bez paniki."
    else:
        transition_note = "Akt 5 (Finał): WAŻNE - Łagodne przejście do praktycznego ćwiczenia na tydzień, przesłania nadziei dla związku i ciepłego słowa końcowego."

    prompt = (
        f"Piszesz scenariusz intymnego i pokrzepiającego odcinka podcastu dla kanału '{config.CHANNEL_NAME}'.\n"
        f"Jedyna prowadząca: {config.HOST1_NAME} (psycholożka i ekspertka od ludzkich relacji, ciepły, empatyczny i życzliwy kobiecy głos).\n"
        f"Format: SOLOWY MONOLOG po polsku, w którym zwraca się bezpośrednio do słuchacza ('ty') jak do drogiej przyjaciółki lub w intymnej konsultacji.\n"
        f"Temat odcinka: {topic_title}\n"
        f"Aktualna sekcja: {act_title}\n"
        f"Fokus emocjonalny: {focus}\n"
        f"Zasada przejścia: {transition_note}\n\n"
        f"WYMAGANIA ŚCISŁE:\n"
        f"- Dokładnie {target_turns} kolejnych replik monologu wypowiadanych przez {config.HOST1_NAME}.\n"
        f"- Każda replika 14-24 słowa, w naturalnym, płynnym, poruszającym i eleganckim stylu mówionym.\n"
        f"- Słownictwo psychologiczne przystępne, pełne życzliwości, niuansów i mądrości emocjonalnej.\n"
        f"- Zwróć WYŁĄCZNIE surową tablicę JSON obiektów (bez markdowna, bez tekstu towarzyszącego):\n"
        f"[\n"
        f"- Każdy obiekt MUSI zawierać także pole \"en\" z naturalnym tłumaczeniem pola \"text\" na język angielski (tylko napisy, nigdy nie wymawiane).\n"
        f'  {{"speaker": "{config.HOST1_SPEAKER}", "name": "{config.HOST1_NAME}", "text": "...", "en": "..."}},\n'
        f'  {{"speaker": "{config.HOST1_SPEAKER}", "name": "{config.HOST1_NAME}", "text": "...", "en": "..."}}\n'
        f"]"
    )

    try:
        resp = requests.post(
            config.POLLINATIONS_ENDPOINT,
            json={
                "model": config.POLLINATIONS_MODEL,
                "messages": [
                    {"role": "system", "content": "Jesteś najwyższej klasy generatorem audycji radiowych i podcastów. Odpowiadasz wyłącznie poprawnym JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.78
            },
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=25
        )
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:].strip()
                raw = raw.split("```")[0].strip()
            parsed = json.loads(raw)
            min_needed = max(2, min(target_turns, 8))
            if isinstance(parsed, list) and len(parsed) >= min_needed:
                result_turns = []
                for p in parsed:
                    txt = p.get("text", "").strip()
                    if not txt:
                        continue
                    result_turns.append({"speaker": config.HOST1_SPEAKER, "name": config.HOST1_NAME, "text": txt, "en": p.get("en", "").strip()})

                # Sanitize repetitive greetings in Acts 2-5
                if act_idx > 0 and result_turns:
                    first_text = result_turns[0]["text"]
                    for prefix in ['witaj', 'witam i zapraszam', 'witaj ponownie', 'cześć wszystkim']:
                        if first_text.lower().startswith(prefix):
                            cleaned = re.sub(r"^(?:witaj(?:\s+ponownie)?(?:\s+na\s+[^.!?]*)?[.!?]\s*|cześć\s+[^.!?]*[.!?]\s*)", "", first_text, flags=re.IGNORECASE).strip()
                            if cleaned:
                                result_turns[0]["text"] = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned
                            else:
                                result_turns[0]["text"] = f"Kontynuujmy naszą refleksję o {topic_title}, przyglądając się naszym codziennym zachowaniom."
                            break

                if len(result_turns) >= target_turns:
                    return result_turns[:target_turns]
                elif len(result_turns) >= min_needed:
                    fallback_turns = generate_curated_fallback_act(act_idx, act_title, topic_title, target_turns=target_turns)
                    seen_texts = set(r["text"] for r in result_turns)
                    for ft in fallback_turns:
                        if len(result_turns) >= target_turns:
                            break
                        if ft["text"] not in seen_texts:
                            result_turns.append(ft)
                            seen_texts.add(ft["text"])
                    return result_turns[:target_turns]
    except Exception as e:
        print(f"  [Uwaga AI] Akt {act_idx+1} powrócił do kuratorowanego scenariusza zapasowego: {e}")
    return None

def generate_full_podcast_story(target_minutes: float = 20.0, topic: str = None, ep_num: int = 1) -> dict:
    history = load_history_topics()
    topic_info = get_next_topic(history, custom_topic=topic, ep_num=ep_num)
    selected_topic = topic_info["topic"]
    acts_meta = topic_info.get("acts", DEFAULT_5_ACTS)

    print(f"[StoryGenerator] Odcinek #{ep_num} - Temat: '{selected_topic}'")

    # Target 20 minutes calibrated with slower -6% speech rate and 0.75s natural pauses (~6.5s per turn)
    turns_per_act = int(max(4, (target_minutes * 60) / (len(acts_meta) * 6.5)))
    if target_minutes <= 1.0:
        turns_per_act = 4
    elif target_minutes <= 3.0:
        turns_per_act = 8

    dialogue = []
    chapters = []

    for act_idx, (act_title, act_focus) in enumerate(acts_meta):
        chapters.append({"title": act_title, "start_turn": len(dialogue)})
        print(f"  [Akt {act_idx+1}/5] Generowanie '{act_title}' ({turns_per_act} replik)...")

        turns = generate_act_ai(act_idx, act_title, selected_topic, act_focus, target_turns=turns_per_act)
        if not turns:
            turns = generate_curated_fallback_act(act_idx, act_title, selected_topic, target_turns=turns_per_act)

        dialogue.extend(turns)

    print(f"[StoryGenerator] Wygenerowano pełny monolog: {len(dialogue)} replik w {len(acts_meta)} aktach.")
    return {
        "topic": selected_topic,
        "thumbnail_title_1": topic_info["thumbnail_title_1"],
        "thumbnail_title_2": topic_info["thumbnail_title_2"],
        "thumbnail_hook": topic_info["thumbnail_hook"],
        "chapters": chapters,
        "dialogue": dialogue
    }

def generate_metadata(topic: str, duration_sec: float, chapters: list, ep_num: int = 1) -> dict:
    title = f"{topic} | {config.CHANNEL_NAME} Odc. {ep_num}"
    lines = [
        f"🎙️ Witaj w {config.CHANNEL_NAME} z {config.HOST1_NAME} - Odcinek #{ep_num}!",
        f"Temat dnia: {topic}",
        "",
        "🕒 ROZDZIAŁY I SYGNATURY CZASOWE:",
    ]
    for ch in chapters:
        m = int(ch.get("start_time", 0) // 60)
        s = int(ch.get("start_time", 0) % 60)
        lines.append(f"{m:02d}:{s:02d} - {ch['title']}")

    clean_tag = config.CHANNEL_NAME.replace(" ", "").replace("'", "")
    lines.extend([
        "",
        "💡 Łagodna i rozjaśniająca podróż do serca psychologii ludzkich relacji, miłości i intymności emocjonalnej.",
        "👉 Subskrybuj, aby co tydzień otrzymywać nowy kojący i inspirujący odcinek.",
    f"#{clean_tag} #Psychologia #Relacje #Miłość #PodcastPoPolsku #RozwójOsobisty #Przywiązanie"
    ])

    return {
        "title": title[:100],
        "description": "\n".join(lines),
        "tags": ["relacje międzyludzkie", "psychologia par", "podcast po polsku", "miłość", "życzliwa komunikacja", "więź emocjonalna", config.CHANNEL_NAME.lower()]
    }

#!/usr/bin/env python3
"""Generate 1,500+ slide-confined practice questions across BIO103 course modules."""
import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1]

STOPWORDS = {
    'this', 'that', 'with', 'from', 'they', 'when', 'what', 'which', 'there', 'their',
    'some', 'each', 'have', 'more', 'also', 'about', 'into', 'only', 'such', 'these',
    'where', 'been', 'were', 'then', 'than', 'will', 'many', 'most', 'other', 'after',
    'because', 'between', 'during', 'through', 'under', 'while', 'small', 'large',
    'first', 'second', 'third', 'total', 'often', 'called', 'cause', 'part', 'type'
}


def clean_line(text):
    return text.strip().lstrip('•▪*1234567890.-– \t').strip()


def generate_all_questions():
    course = json.loads((APP / 'data/course.json').read_text())
    
    total_generated = 0
    
    for m in course['modules']:
        mod_id = m['id']
        lecture = m['lectureLabel']
        slides = m['slides']
        cards = m['flashcards']
        questions = []
        seen_prompts = set()
        
        # 1. Existing Forward Term Matching Questions (from flashcards)
        for idx, card in enumerate(cards):
            alternatives = [c['term'] for c in cards if c['term'] != card['term']]
            if len(alternatives) >= 3:
                dists = alternatives[idx % len(alternatives):] + alternatives[:idx % len(alternatives)]
                selected_dists = dists[:3]
                correct_idx = idx % 4
                opts = selected_dists[:]
                opts.insert(correct_idx, card['term'])
                
                term_pattern = r'(?<!\w)' + r'\s+'.join(re.escape(x) for x in card['term'].split()) + r'(?!\w)'
                prompt_quote, blanks = re.subn(term_pattern, '________', card['definition'], flags=re.I)
                stem = 'Which slide term completes this description?' if blanks else 'Which slide term matches this description?'
                prompt = f"{stem}\n\n“{prompt_quote}”"
                seen_prompts.add(prompt)
                questions.append({
                    'id': f"{mod_id}-fwd-{idx+1:03d}",
                    'prompt': prompt,
                    'promptStyle': 'cloze' if blanks else 'matching',
                    'options': opts,
                    'correctIndex': correct_idx,
                    'explanation': card['definition'],
                    'slideId': card['slideId'],
                    'page': card['page'],
                    'sourceQuote': card['definition'],
                    'sourceCardId': card['id'],
                })
            
        # 2. Reverse Concept Definition Questions
        for idx, card in enumerate(cards):
            others = [c for c in cards if c['id'] != card['id'] and c['definition'] != card['definition']]
            if len(others) >= 3:
                correct_idx = (idx + 1) % 4
                opts = [c['definition'] for c in others[:3]]
                opts.insert(correct_idx, card['definition'])
                prompt = f"According to {lecture} (Slide {card['page']}), what is the slide definition of “{card['term']}”?"
                if prompt not in seen_prompts:
                    seen_prompts.add(prompt)
                    questions.append({
                        'id': f"{mod_id}-rev-{idx+1:03d}",
                        'prompt': prompt,
                        'promptStyle': 'reverse-matching',
                        'options': opts,
                        'correctIndex': correct_idx,
                        'explanation': card['definition'],
                        'slideId': card['slideId'],
                        'page': card['page'],
                        'sourceQuote': card['definition'],
                        'sourceCardId': card['id'],
                    })
        
        # 3. Slide-Fact Cloze Questions using Module Vocabulary & Flashcard Terms
        vocab = [c['term'] for c in cards]
        for s in slides:
            for p in s['paragraphs']:
                for line in p.split('\n'):
                    for match in re.findall(r'\b[A-Z][a-z]{3,15}\b', line):
                        if match.lower() not in STOPWORDS and match not in vocab:
                            vocab.append(match)
        
        cloze_idx = 0
        for s in slides:
            for p in s['paragraphs']:
                lines = [clean_line(l) for l in p.split('\n') if clean_line(l)]
                for line in lines:
                    words = line.split()
                    if not (4 <= len(words) <= 35):
                        continue
                    if any(k in line.lower() for k in ['copyright', 'lecture', 'thank you', 'http', 'page']):
                        continue
                    for term in vocab:
                        pat = r'(?<!\w)' + re.escape(term) + r'(?!\w)'
                        if re.search(pat, line, re.I):
                            blanked, cnt = re.subn(pat, '________', line, flags=re.I)
                            if cnt == 1:
                                dists = [t for t in vocab if t.lower() != term.lower() and abs(len(t) - len(term)) <= 8]
                                if len(dists) >= 3:
                                    correct_idx = cloze_idx % 4
                                    opts = dists[:3]
                                    opts.insert(correct_idx, term)
                                    if len(set(opts)) == 4:
                                        prompt = f"Which term completes this excerpt from {lecture} (Slide {s['number']})?\n\n“{blanked}”"
                                        if prompt not in seen_prompts:
                                            seen_prompts.add(prompt)
                                            cloze_idx += 1
                                            questions.append({
                                                'id': f"{mod_id}-cloze-{cloze_idx:03d}",
                                                'prompt': prompt,
                                                'promptStyle': 'fact-cloze',
                                                'options': opts,
                                                'correctIndex': correct_idx,
                                                'explanation': line,
                                                'slideId': s['id'],
                                                'page': s['number'],
                                                'sourceQuote': line,
                                            })
                            break

        # 4. Slide Statement Verification Questions
        slide_statements = []
        for s in slides:
            for p in s['paragraphs']:
                for raw_l in p.split('\n'):
                    l = clean_line(raw_l)
                    words = l.split()
                    if 4 <= len(words) <= 26 and not any(k in l.lower() for k in ['copyright', 'lecture', 'thank you', 'http']):
                        if len(l) >= 12:
                            slide_statements.append((s['id'], s['number'], s['title'], l))
        
        stmt_idx = 0
        for s_id, s_num, s_title, stmt in slide_statements:
            other_stmts = [other[3] for other in slide_statements if other[1] != s_num and other[3] != stmt and len(other[3]) >= 12]
            if len(other_stmts) >= 3:
                start_i = (stmt_idx * 5) % len(other_stmts)
                dists = other_stmts[start_i:] + other_stmts[:start_i]
                selected_dists = []
                for d in dists:
                    if d not in selected_dists and d != stmt:
                        selected_dists.append(d)
                    if len(selected_dists) == 3:
                        break
                if len(selected_dists) == 3:
                    correct_idx = stmt_idx % 4
                    opts = selected_dists[:]
                    opts.insert(correct_idx, stmt)
                    title_hint = f" ({s_title})" if s_title else ""
                    prompt = f"Which statement is directly excerpted from Slide {s_num}{title_hint} of {lecture}?"
                    if prompt not in seen_prompts:
                        seen_prompts.add(prompt)
                        stmt_idx += 1
                        questions.append({
                            'id': f"{mod_id}-stmt-{stmt_idx:03d}",
                            'prompt': prompt,
                            'promptStyle': 'statement-verification',
                            'options': opts,
                            'correctIndex': correct_idx,
                            'explanation': f"Slide {s_num}: “{stmt}”",
                            'slideId': s_id,
                            'page': s_num,
                            'sourceQuote': stmt,
                        })

        m['quiz'] = questions
        total_generated += len(questions)
        print(f"Module {mod_id}: {len(questions)} questions")
        
    course['stats']['quizCount'] = total_generated
    (APP / 'data/course.json').write_text(json.dumps(course, ensure_ascii=False, indent=2))
    print(f"\nSuccessfully generated {total_generated} questions across all modules!")
    return total_generated


if __name__ == '__main__':
    generate_all_questions()

# Estrae il copione di Marvelous dalla ROM inglese.
# uso: python3 estrai_m.py rom_inglese.sfc copione_it.txt
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marv as M

HEADER = """\
# ============================================================================
#  MARVELOUS: ANOTHER TREASURE ISLAND - copione per la traduzione italiana
# ============================================================================
#  Ogni voce inizia con  ### nnnn  (non modificare, non aggiungere, non
#  togliere voci: il gioco le ritrova contandole).
#  Le righe ;EN sono riferimento e vengono ignorate.
#
#  CODICI
#   1| 2| 3|   = inizio della riga 1, 2 o 3 della finestra (uno per riga)
#   <P>        = attende il tasto e pulisce la finestra
#   <FB> <FA>  = fine voce: devono restare alla fine, uguali all'originale
#   <..>       = altri comandi del gioco (nomi, pause, eventi): lasciali
#  REGOLE
#   - Ogni riga deve stare in 256 unita' di larghezza (circa 22 lettere);
#     il compilatore avvisa se sfori.
#   - Lettere accentate: à è é ì ò ù. Per È scrivi E'.
#   - Gli a-capo nel file servono solo alla leggibilita': contano i codici.
# ============================================================================

"""

def main(rom, out):
    d = open(rom, 'rb').read()
    entries, end = M.parse(d)
    o = [HEADER]
    for n, toks in enumerate(entries):
        t = M.toks_to_text(toks, M.EN_TABLE)
        o.append('### %04d\n' % n)
        for line in t.split('\n'):
            o.append(';EN ' + line + '\n')
        o.append(t.lstrip('\n') + '\n\n')
    open(out, 'w', encoding='utf-8').write(''.join(o))
    print('voci', len(entries), 'fine copione %06X' % end)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

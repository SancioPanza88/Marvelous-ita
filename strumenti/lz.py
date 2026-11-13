def lz_decomp(d, i, big=False, maxout=0x10000):
    out = bytearray(); st = i
    while i < len(d) and len(out) < maxout:
        b = d[i]; i += 1
        if b == 0xFF: return bytes(out), i - st
        cmd = b >> 5; n = (b & 0x1F) + 1
        if cmd == 7:
            cmd = (b >> 2) & 7; n = (((b & 3) << 8) | d[i]) + 1; i += 1
            if cmd == 7: return None, 0
        if cmd == 0: out += d[i:i + n]; i += n
        elif cmd == 1: out += bytes([d[i]]) * n; i += 1
        elif cmd == 2:
            w = d[i:i + 2]; i += 2
            out += (w * ((n + 1) // 2))[:n]
        elif cmd == 3:
            v = d[i]; i += 1; out += bytes((v + k) & 255 for k in range(n))
        elif cmd == 4:
            o = (d[i] << 8 | d[i + 1]) if big else (d[i] | d[i + 1] << 8); i += 2
            if o >= len(out): return None, 0
            for k in range(n): out.append(out[o + k])
        else: return None, 0
    return None, 0

def _hdr(cmd, n):
    n -= 1
    if n < 32: return bytes([(cmd << 5) | n])
    return bytes([0xE0 | (cmd << 2) | (n >> 8), n & 0xFF])

def lz_comp(data, big=True):
    """Compressore greedy compatibile con lz_decomp (offset assoluti)."""
    out = bytearray(); lit = bytearray(); i = 0; N = len(data)
    # indice per trovare match: dizionario di sequenze da 3 byte
    idx = {}
    def flush():
        nonlocal lit
        while lit:
            ch = lit[:1024]; out.extend(_hdr(0, len(ch))); out.extend(ch); lit = lit[1024:]
    def add(p):
        if p + 3 <= N: idx.setdefault(bytes(data[p:p+3]), []).append(p)
    while i < N:
        best = (0, None, 0)  # (gain, cmd, len, arg)
        # byte fill
        n = 1
        while i + n < N and n < 1024 and data[i + n] == data[i]: n += 1
        cand = [(n - 2, 1, n, data[i:i+1])]
        # word fill
        if i + 1 < N:
            n = 2
            while i + n < N and n < 1024 and data[i + n] == data[i + (n % 2)]: n += 1
            cand.append((n - 3, 2, n, data[i:i+2]))
        # increasing
        n = 1
        while i + n < N and n < 1024 and data[i + n] == (data[i] + n) & 255: n += 1
        cand.append((n - 2, 3, n, data[i:i+1]))
        # copy
        key = bytes(data[i:i+3]); bl = 0; bo = 0
        for p in idx.get(key, [])[-64:]:
            n = 0
            while i + n < N and n < 1024 and data[p + n] == data[i + n]: n += 1
            if n > bl: bl, bo = n, p
        if bl >= 3:
            ob = bytes([bo >> 8, bo & 255]) if big else bytes([bo & 255, bo >> 8])
            cand.append((bl - 3, 4, bl, ob))
        g, cmd, n, arg = max(cand, key=lambda c: c[0])
        if g > 0 or (cmd != 4 and g >= 0 and n >= 3):
            flush(); out.extend(_hdr(cmd, n)); out.extend(arg)
            for k in range(n): add(i + k)
            i += n
        else:
            lit.append(data[i]); add(i); i += 1
    flush(); out.append(0xFF)
    return bytes(out)

def lz_comp_opt(data, big=True):
    """Compressore a parsing ottimale (programmazione dinamica)."""
    N = len(data); INF = 10**9
    idx = {}
    for p in range(N - 2): idx.setdefault(bytes(data[p:p+3]), []).append(p)
    # migliori opzioni per posizione
    match = [(0, 0)] * N
    for i in range(N):
        bl = bo = 0
        for p in idx.get(bytes(data[i:i+3]), []):
            if p >= i: break
            n = 0
            while i + n < N and n < 1024 and data[p + n] == data[i + n]: n += 1
            if n > bl: bl, bo = n, p
        match[i] = (bl, bo)
    rb = [0] * (N + 1); rw = [0] * (N + 1); ri = [0] * (N + 1)
    for i in range(N - 1, -1, -1):
        rb[i] = 1 + (rb[i + 1] if i + 1 < N and data[i + 1] == data[i] else 0)
        rb[i] = min(rb[i], 1024)
        ri[i] = 1 + (ri[i + 1] if i + 1 < N and data[i + 1] == (data[i] + 1) & 255 else 0)
        ri[i] = min(ri[i], 1024)
    for i in range(N):
        n = 2 if i + 1 < N else 0
        if n:
            while i + n < N and n < 1024 and data[i + n] == data[i + (n % 2)]: n += 1
        rw[i] = n
    hc = lambda n: 1 if n <= 32 else 2
    cost = [INF] * (N + 1); choice = [None] * (N + 1); cost[N] = 0
    for i in range(N - 1, -1, -1):
        best = INF; ch = None
        for n in range(1, min(1024, N - i) + 1):
            if n > 64 and n % 32: continue
            c = hc(n) + n + cost[i + n]
            if c < best: best, ch = c, (0, n, None)
        for n in range(2, rb[i] + 1):
            c = hc(n) + 1 + cost[i + n]
            if c < best: best, ch = c, (1, n, None)
        for n in range(3, rw[i] + 1):
            c = hc(n) + 2 + cost[i + n]
            if c < best: best, ch = c, (2, n, None)
        for n in range(2, ri[i] + 1):
            c = hc(n) + 1 + cost[i + n]
            if c < best: best, ch = c, (3, n, None)
        bl, bo = match[i]
        for n in range(3, bl + 1):
            c = hc(n) + 2 + cost[i + n]
            if c < best: best, ch = c, (4, n, bo)
        cost[i] = best; choice[i] = ch
    out = bytearray(); i = 0
    while i < N:
        cmd, n, bo = choice[i]
        out += _hdr(cmd, n)
        if cmd == 0: out += data[i:i+n]
        elif cmd == 1: out.append(data[i])
        elif cmd == 2: out += data[i:i+2]
        elif cmd == 3: out.append(data[i])
        else: out += bytes([bo >> 8, bo & 255]) if big else bytes([bo & 255, bo >> 8])
        i += n
    out.append(0xFF)
    return bytes(out)

def parse_bcd(line) :
    """
    Parses a line of the pbd and returns a dictionary of candidate promoters,
    with their probabilities
    """
    bcd,all_candidates = line.strip().split('\t')
    d = {}
    for candidates in all_candidates.split(';') :
        for candidate in candidates.split(',') :
            prom_name,p = candidate.split(':')
            d[prom_name] = p
    return d

numProgrammers, numArtists, numApplications = map(int, input().split())
skills = [] # holds (programSkill, artSkill)
for _ in range(n):
    programSkill, artSkill = map(int, input().split())
    skills.append([programSkill, artSkill])
skills.sort(reverse=True) # descending order of program skill
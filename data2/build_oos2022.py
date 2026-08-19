#!/usr/bin/env python3
"""Assemble oos2022.json from data transcribed via WebFetch (2026-08-16).
Sources quoted verbatim; only arithmetic is the half-PPR -> PPR projection adjustment."""
import json

# ---------------- ADP: FantasyFootballCalculator PPR 12-team 2022 (157 rows incl DEF/PK) ----------------
ADP_RAW = """1|Jonathan Taylor|RB|IND|1.3
2|Christian McCaffrey|RB|SF|2.4
3|Austin Ekeler|RB|LAC|2.7
4|Derrick Henry|RB|TEN|4.3
5|Justin Jefferson|WR|MIN|4.6
6|Cooper Kupp|WR|LAR|5.7
7|Najee Harris|RB|PIT|7.1
8|Dalvin Cook|RB|MIN|7.5
9|Ja'Marr Chase|WR|CIN|8.7
10|Joe Mixon|RB|CIN|10.1
11|Alvin Kamara|RB|NO|10.9
12|Davante Adams|WR|LV|12.0
13|D'Andre Swift|RB|DET|12.8
14|Stefon Diggs|WR|BUF|13.6
15|Aaron Jones Sr.|RB|GB|14.9
16|Saquon Barkley|RB|NYG|15.5
17|Travis Kelce|TE|KC|16.5
18|CeeDee Lamb|WR|DAL|17.5
19|Nick Chubb|RB|CLE|18.8
20|Deebo Samuel Sr.|WR|SF|19.6
21|Javonte Williams|RB|DEN|20.2
22|Josh Allen|QB|BUF|20.4
23|Leonard Fournette|RB|TB|21.9
24|Tyreek Hill|WR|MIA|22.7
25|Michael Pittman Jr.|WR|IND|24.9
26|Mark Andrews|TE|BAL|25.5
27|Mike Evans|WR|TB|26.5
28|Ezekiel Elliott|RB|DAL|27.7
29|James Conner|RB|ARI|28.4
30|Keenan Allen|WR|LAC|29.5
31|A.J. Brown|WR|PHI|30.4
32|Kyle Pitts Sr.|TE|ATL|31.2
33|Tee Higgins|WR|CIN|32.5
34|Cam Akers|RB|LAR|33.1
35|Justin Herbert|QB|LAC|33.2
36|Travis Etienne Jr.|RB|JAX|33.6
37|DJ Moore|WR|CAR|35.9
38|Terry McLaurin|WR|WAS|38.0
39|Patrick Mahomes|QB|KC|38.3
40|J.K. Dobbins|RB|BAL|38.8
41|David Montgomery|RB|CHI|39.3
42|Mike Williams|WR|LAC|39.6
43|Elijah Mitchell|RB|SF|42.4
44|Diontae Johnson|WR|PIT|43.4
45|George Kittle|TE|SF|44.2
46|Breece Hall|RB|NYJ|44.4
47|Courtland Sutton|WR|DEN|45.3
48|Joe Burrow|QB|CIN|46.1
49|Josh Jacobs|RB|LV|46.8
50|Jaylen Waddle|WR|MIA|47.7
51|AJ Dillon|RB|GB|48.7
52|Darren Waller|TE|LV|50.4
53|Lamar Jackson|QB|BAL|51.3
54|DK Metcalf|WR|SEA|51.4
55|Michael Thomas|WR|NO|52.3
56|Allen Robinson II|WR|LAR|53.5
57|Clyde Edwards-Helaire|RB|KC|54.3
58|Jalen Hurts|QB|PHI|56.3
59|Chris Godwin Jr.|WR|TB|56.5
60|Brandin Cooks|WR|HOU|56.7
61|Damien Harris|RB|NE|59.8
62|Kyler Murray|QB|ARI|61.6
63|Jerry Jeudy|WR|DEN|61.7
64|Miles Sanders|RB|PHI|61.7
65|Dalton Schultz|TE|DAL|62.6
66|Gabe Davis|WR|BUF|62.9
67|Rashaad Penny|RB|SEA|63.3
68|Adam Thielen|WR|MIN|63.8
69|Darnell Mooney|WR|CHI|68.1
70|Hollywood Brown|WR|ARI|68.7
71|Kareem Hunt|RB|CLE|68.9
72|Chase Edmonds|RB|DEN|69.6
73|Dameon Pierce|RB|HOU|70.5
74|Tony Pollard|RB|DAL|70.8
75|Hunter Renfrow|WR|LV|71.2
76|Russell Wilson|QB|DEN|72.5
77|Amon-Ra St. Brown|WR|DET|73.4
78|Devin Singletary|RB|BUF|74.4
79|Dallas Goedert|TE|PHI|75.2
80|JuJu Smith-Schuster|WR|KC|75.9
81|Rhamondre Stevenson|RB|NE|76.0
82|Aaron Rodgers|QB|GB|80.2
83|Rashod Bateman|WR|BAL|81.0
84|Dak Prescott|QB|DAL|83.6
85|Amari Cooper|WR|CLE|84.2
86|Melvin Gordon III|RB|KC|85.4
87|DeVonta Smith|WR|PHI|86.6
88|Tom Brady|QB|TB|86.8
89|Elijah Moore|WR|NYJ|87.9
90|Zach Ertz|TE|ARI|89.0
91|Allen Lazard|WR|GB|89.5
92|DeAndre Hopkins|WR|ARI|90.0
93|Brandon Aiyuk|WR|SF|90.0
94|Matthew Stafford|QB|LAR|90.3
95|Cordarrelle Patterson|RB|ATL|91.4
96|James Cook III|RB|BUF|92.0
97|Kenneth Walker|RB|SEA|92.9
98|Nyheim Hines|RB|BUF|93.9
99|Christian Kirk|WR|JAX|96.2
100|Trey Lance|QB|SF|97.7
101|Pat Freiermuth|TE|PIT|100.0
102|James Robinson|RB|NYJ|101.5
103|Raheem Mostert|RB|MIA|101.9
104|Drake London|WR|ATL|102.2
105|Robert Woods|WR|TEN|102.5
106|Kadarius Toney|WR|KC|102.7
107|Derek Carr|QB|LV|103.1
108|Cole Kmet|TE|CHI|103.6
109|Kenny Gainwell|RB|PHI|105.8
110|Tyler Allgeier|RB|ATL|107.6
111|Kirk Cousins|QB|MIN|108.6
112|J.D. McKissic|RB|WAS|110.2
113|Chris Olave|WR|NO|110.4
114|Dawson Knox|TE|BUF|111.5
115|Darrell Henderson Jr.|RB|JAX|111.9
116|Tyler Lockett|WR|SEA|112.5
117|Brian Robinson|RB|WAS|112.7
118|Michael Carter|RB|NYJ|113.3
119|Antonio Gibson|RB|WAS|114.7
120|Buffalo Defense|DEF|BUF|117.2
121|Isiah Pacheco|RB|KC|118.0
122|Skyy Moore|WR|KC|118.1
123|Michael Gallup|WR|DAL|118.2
124|T.J. Hockenson|TE|MIN|120.2
125|Julio Jones|WR|TB|120.9
126|Tua Tagovailoa|QB|MIA|121.2
127|Jamaal Williams|RB|DET|121.7
128|Tyler Boyd|WR|CIN|123.0
129|Rachaad White|RB|TB|123.3
130|George Pickens|WR|PIT|123.6
131|Alexander Mattison|RB|MIN|128.9
132|Marquez Valdes-Scantling|WR|KC|129.0
133|Treylon Burks|WR|TEN|129.3
134|Zamir White|RB|LV|130.5
135|LA Rams Defense|DEF|LAR|131.5
136|Matt Ryan|QB|IND|132.9
137|Chase Claypool|WR|CHI|133.7
138|Romeo Doubs|WR|GB|134.1
139|Hunter Henry|TE|NE|134.1
140|DeVante Parker|WR|NE|134.9
141|Justin Tucker|PK|BAL|135.5
142|Justin Fields|QB|CHI|138.0
143|Daniel Carlson|PK|LV|139.4
144|Rondale Moore|WR|ARI|142.5
145|Trevor Lawrence|QB|JAX|142.9
146|Tampa Bay Defense|DEF|TB|143.5
147|Tyler Bass|PK|BUF|143.7
148|San Francisco Defense|DEF|SF|144.1
149|Indianapolis Defense|DEF|IND|145.6
150|Irv Smith Jr.|TE|MIN|146.0
151|Robert Tonyan|TE|GB|147.9
152|Jameis Winston|QB|NO|150.1
153|Isaiah McKenzie|WR|BUF|152.6
154|LA Chargers Defense|DEF|LAC|153.7
155|Nico Collins|WR|HOU|153.8
156|Matt Gay|PK|LAR|159.1
157|Dustin Hopkins|PK|LAC|159.5"""

# ---------------- Projections: FFToday 2022, FPts = FFToday Half-PPR ----------------
# QB: Name|Team|FPts  (no receptions; PPR == half-PPR for QBs)
PROJ_QB = """Josh Allen|BUF|416.1
Justin Herbert|LAC|372.3
Patrick Mahomes|KC|372.2
Tom Brady|TB|356.2
Kyler Murray|ARI|350.7
Dak Prescott|DAL|346.5
Jalen Hurts|PHI|340.3
Lamar Jackson|BAL|333.4
Joe Burrow|CIN|321.7
Matthew Stafford|LAR|318.1
Aaron Rodgers|GB|316.5
Kirk Cousins|MIN|315.9
Russell Wilson|DEN|314.5
Trey Lance|SF|303.7
Derek Carr|LV|296.9
Ryan Tannehill|TEN|289.4
Justin Fields|CHI|286.1
Trevor Lawrence|JAC|283.2
Tua Tagovailoa|MIA|280.4
Zach Wilson|NYJ|271.6
Matt Ryan|IND|263.6
Jared Goff|DET|261.9
Mac Jones|NE|254.0
Carson Wentz|WAS|253.2
Daniel Jones|NYG|252.7
Davis Mills|HOU|244.5
Baker Mayfield|CAR|242.5
Jameis Winston|NO|195.7
Marcus Mariota|ATL|180.4
Jacoby Brissett|CLE|167.5
Geno Smith|SEA|156.3
Kenny Pickett|PIT|155.9"""

# RB/WR/TE: Name|Team|Rec|FPts(half-PPR)  ->  PPR = FPts + 0.5*Rec
PROJ_RB = """Jonathan Taylor|IND|39|304.4
Christian McCaffrey|CAR|85|278.6
Austin Ekeler|LAC|76|269.7
Derrick Henry|TEN|20|257.8
Najee Harris|PIT|59|237.0
Alvin Kamara|NO|60|234.9
Dalvin Cook|MIN|42|231.9
Joe Mixon|CIN|40|230.9
Leonard Fournette|TB|62|225.7
Saquon Barkley|NYG|56|221.0
James Conner|ARI|47|217.7
D'Andre Swift|DET|65|212.5
Javonte Williams|DEN|44|210.0
Aaron Jones|GB|63|209.4
Nick Chubb|CLE|24|207.0
Ezekiel Elliott|DAL|45|204.2
David Montgomery|CHI|46|201.5
Elijah Mitchell|SF|22|193.9
Cam Akers|LAR|30|193.1
Breece Hall|NYJ|36|192.0
Cordarrelle Patterson|ATL|46|179.3
Damien Harris|NE|16|177.8
Josh Jacobs|LV|39|176.7
Travis Etienne|JAC|48|176.7
Dameon Pierce|HOU|34|173.9
J.K. Dobbins|BAL|32|170.6
Tony Pollard|DAL|49|167.5
Miles Sanders|PHI|32|166.8
AJ Dillon|GB|37|163.8
Chase Edmonds|MIA|51|163.6
Clyde Edwards-Helaire|KC|36|163.1
Devin Singletary|BUF|38|162.1
Rhamondre Stevenson|NE|34|160.5
Antonio Gibson|WAS|30|156.5
Kareem Hunt|CLE|42|152.5
Melvin Gordon|DEN|24|142.0
Rashaad Penny|SEA|20|140.7
Nyheim Hines|IND|53|126.4
Michael Carter|NYJ|43|122.9
James Robinson|JAC|23|119.6
James Cook|BUF|40|117.5
Jamaal Williams|DET|26|113.7
Raheem Mostert|MIA|16|112.3
Kenneth Walker|SEA|15|110.3
Kenneth Gainwell|PHI|35|104.7
J.D. McKissic|WAS|49|103.2
Darrell Henderson|LAR|26|97.4
Alexander Mattison|MIN|28|96.9
Rex Burkhead|HOU|28|84.7
Mark Ingram|NO|20|84.3
Ameer Abdullah|LV|41|81.3
Brian Robinson Jr.|WAS|14|79.2
Damien Williams|ATL|27|78.9
Gus Edwards|BAL|5|78.0
Rachaad White|TB|15|75.4
Jerick McKinnon|KC|30|72.1
Khalil Herbert|CHI|17|70.7
Matt Breida|NYG|14|67.7
Zamir White|LV|7|66.7
Samaje Perine|CIN|26|65.4
Boston Scott|PHI|10|64.7
Kyle Juszczyk|SF|38|60.6
Dontrell Hilliard|TEN|21|59.5
D'Onta Foreman|CAR|5|59.0
Eno Benjamin|ARI|10|58.4
Isaiah Spiller|LAC|14|57.1
Tyler Allgeier|ATL|9|53.8
Isiah Pacheco|KC|6|53.6
Sony Michel|LAC|8|53.2
Jeff Wilson|SF|12|49.8
D'Ernest Johnson|CLE|10|48.9
Chuba Hubbard|CAR|20|47.0
Ke'Shawn Vaughn|TB|6|43.4
Travis Homer|SEA|16|41.0
Ronald Jones|KC|4|40.2
Chris Evans|CIN|20|38.3
Tyrion Davis-Price|SF|3|37.3
Mike Davis|BAL|3|37.1
Brandon Bolden|LV|12|36.4
Benny Snell|PIT|5|35.4
Joshua Kelley|LAC|3|32.7
Kenyan Drake|BAL|6|30.5
Darrel Williams|ARI|5|30.2
Snoop Conner|JAC|8|30.0
Craig Reynolds|DET|6|29.0
Gary Brightwell|NYG|7|28.2
Hassan Haskins|TEN|3|28.0
Myles Gaskin|MIA|9|27.9
Jaylen Warren|PIT|4|25.8
Zack Moss|BUF|4|25.3
Tony Jones|NO|5|24.7
Kyren Williams|LAR|7|23.3
Giovani Bernard|TB|8|22.8
Ty Montgomery|NE|6|16.2"""

PROJ_WR = """Cooper Kupp|LAR|109|269.8
Justin Jefferson|MIN|92|245.3
Ja'Marr Chase|CIN|83|237.0
Stefon Diggs|BUF|98|222.7
CeeDee Lamb|DAL|87|216.5
Davante Adams|LV|90|215.6
Tyreek Hill|MIA|82|213.1
Deebo Samuel|SF|59|203.2
Mike Evans|TB|72|197.5
Keenan Allen|LAC|100|191.0
Tee Higgins|CIN|78|189.7
Michael Pittman Jr.|IND|84|187.3
Brandin Cooks|HOU|87|187.3
D.J. Moore|CAR|85|185.8
Mike Williams|LAC|72|185.6
Diontae Johnson|PIT|91|185.0
A.J. Brown|PHI|80|184.0
Darnell Mooney|CHI|83|183.3
Amon-Ra St. Brown|DET|87|181.4
DK Metcalf|SEA|76|178.8
Terry McLaurin|WAS|80|177.7
Courtland Sutton|DEN|70|177.4
Jerry Jeudy|DEN|76|176.9
JuJu Smith-Schuster|KC|71|168.2
Chris Godwin|TB|71|166.3
Michael Thomas|NO|82|163.7
Gabe Davis|BUF|58|162.5
Rashod Bateman|BAL|74|159.4
Adam Thielen|MIN|69|157.8
Allen Robinson|LAR|74|156.9
Hunter Renfrow|LV|82|156.6
Jaylen Waddle|MIA|71|156.2
Elijah Moore|NYJ|71|154.1
Christian Kirk|JAC|69|153.1
Drake London|ATL|66|151.5
Amari Cooper|CLE|66|150.9
Tyler Lockett|SEA|67|150.9
Kadarius Toney|NYG|65|150.7
Robert Woods|TEN|66|147.4
Allen Lazard|GB|59|144.0
Marquise Brown|ARI|65|143.0
Russell Gage|TB|60|140.4
Tyler Boyd|CIN|62|137.3
Brandon Aiyuk|SF|58|137.1
DeAndre Hopkins|ARI|54|135.1
Nico Collins|HOU|58|133.4
Chase Claypool|PIT|62|131.7
Chris Olave|NO|54|131.2
Jakobi Meyers|NE|60|130.4
Mecole Hardman|KC|53|128.3
Treylon Burks|TEN|54|128.3
Kenny Golladay|NYG|51|125.7
DeVonta Smith|PHI|53|124.9
Robbie Chosen|CAR|58|124.9
Van Jefferson|LAR|50|121.8
DeVante Parker|NE|52|121.5
Garrett Wilson|NYJ|57|119.2
Marquez Valdes-Scantling|KC|45|118.2
George Pickens|PIT|56|116.5
Rondale Moore|ARI|53|114.4
Curtis Samuel|WAS|43|112.3
Michael Gallup|DAL|47|111.6
Jahan Dotson|WAS|51|109.0
Jarvis Landry|NO|46|108.6
Skyy Moore|KC|45|106.9
Jalen Tolbert|DAL|45|104.1
KJ Hamler|DEN|45|103.1
Romeo Doubs|GB|43|102.0
Corey Davis|NYJ|40|99.5
K.J. Osborn|MIN|43|98.8
Josh Palmer|LAC|41|98.8
Marvin Jones|JAC|47|97.0
Isaiah McKenzie|BUF|48|94.9
Parris Campbell|IND|40|91.7
Julio Jones|TB|35|89.4
Zay Jones|JAC|40|89.0
Alec Pierce|IND|35|86.0
Jameson Williams|DET|37|85.6
Christian Watson|GB|34|85.5
Devin Duvernay|BAL|46|83.5
Wan'Dale Robinson|NYG|37|83.0
D.J. Chark|DET|32|82.6
Nick Westbrook-Ikhine|TEN|37|82.0
Donovan Peoples-Jones|CLE|32|80.8
Velus Jones Jr.|CHI|33|80.2
Cedrick Wilson|MIA|35|78.8
Randall Cobb|GB|34|78.0
Braxton Berrios|NYJ|41|76.2
Sammy Watkins|GB|32|75.1
A.J. Green|ARI|33|74.3
Nelson Agholor|NE|34|73.3
Dee Eskridge|SEA|29|66.6
James Washington|DAL|25|63.0
Sterling Shepard|NYG|28|62.7
Olamide Zaccheaus|ATL|28|62.5
Byron Pringle|CHI|27|60.4
Jamison Crowder|BUF|30|60.1
Anthony Schwartz|CLE|25|60.1
Terrace Marshall Jr.|CAR|28|58.9
Quez Watkins|PHI|24|56.8"""

PROJ_TE = """Mark Andrews|BAL|88|202.4
Travis Kelce|KC|82|190.4
Kyle Pitts|ATL|72|170.9
Darren Waller|LV|77|157.0
George Kittle|SF|67|152.8
Dalton Schultz|DAL|76|151.7
T.J. Hockenson|DET|68|135.1
Dallas Goedert|PHI|62|133.7
Zach Ertz|ARI|64|129.7
Cole Kmet|CHI|68|125.7
Hunter Henry|NE|54|123.7
Dawson Knox|BUF|50|121.5
Tyler Higbee|LAR|56|117.0
Pat Freiermuth|PIT|60|116.7
Mike Gesicki|MIA|57|113.7
Albert Okwuegbunam|DEN|52|113.4
David Njoku|CLE|61|112.1
Austin Hooper|TEN|54|107.6
Irv Smith|MIN|46|107.4
Logan Thomas|WAS|53|107.2
Noah Fant|SEA|53|102.0
Robert Tonyan|GB|47|99.8
Evan Engram|JAC|48|98.1
Gerald Everett|LAC|46|95.2
Brevin Jordan|HOU|45|84.0
Mo Alie-Cox|IND|38|81.6
Hayden Hurst|CIN|40|80.2
C.J. Uzomah|NYJ|40|78.7
Jonnu Smith|NE|37|76.7
Isaiah Likely|BAL|36|74.4
Cameron Brate|TB|38|73.5
Harrison Bryant|CLE|35|66.0"""

# ---------------- Actuals: FantasyPros 2022 season stats, scoring=PPR (Name (Team)|G|FPTS) ----------------
ACT_QB = """Patrick Mahomes II (KC)|17|429.4
Josh Allen (BUF)|17|412.4
Jalen Hurts (PHI)|15|384.1
Joe Burrow (CIN)|17|369.0
Geno Smith (SEA)|17|314.9
Justin Fields (CHI)|15|307.0
Kirk Cousins (MIN)|17|305.6
Trevor Lawrence (JAC)|17|303.7
Daniel Jones (NYG)|16|293.9
Jared Goff (DET)|17|291.3
Justin Herbert (LAC)|17|291.3
Tom Brady (TB)|17|280.5
Aaron Rodgers (GB)|17|251.3
Lamar Jackson (BAL)|12|243.1
Tua Tagovailoa (MIA)|13|239.0
Russell Wilson (DEN)|15|237.0
Derek Carr (LV)|15|233.0
Dak Prescott (DAL)|12|213.6
Kyler Murray (ARI)|11|207.6
Marcus Mariota (ATL)|13|205.7
Davis Mills (HOU)|15|196.5
Andy Dalton (NO)|14|183.3
Mac Jones (NE)|14|181.1
Jacoby Brissett (CLE)|14|174.7
Jimmy Garoppolo (SF)|11|168.7
Matt Ryan (IND)|12|168.3
Ryan Tannehill (TEN)|12|167.2
Kenny Pickett (PIT)|13|159.0
Baker Mayfield (LAR)|12|129.4
Taylor Heinicke (WAS)|9|121.9
Carson Wentz (WAS)|8|121.8
Matthew Stafford (LAR)|9|116.5
Brock Purdy (SF)|9|110.3
Zach Wilson (NYJ)|9|106.0
Deshaun Watson (CLE)|6|90.5
Sam Darnold (CAR)|6|89.3
Mitchell Trubisky (PIT)|7|79.0
Mike White (NYJ)|4|60.6"""

ACT_RB = """Austin Ekeler (LAC)|17|372.7
Christian McCaffrey (SF)|17|356.4
Josh Jacobs (LV)|17|328.3
Derrick Henry (TEN)|16|302.8
Saquon Barkley (NYG)|16|284.0
Nick Chubb (CLE)|17|281.4
Rhamondre Stevenson (NE)|17|249.1
Tony Pollard (DAL)|16|248.8
Aaron Jones Sr. (GB)|17|248.6
Joe Mixon (CIN)|15|240.7
Dalvin Cook (MIN)|17|237.8
Leonard Fournette (TB)|16|227.1
Jamaal Williams (DET)|17|225.9
Najee Harris (PIT)|17|223.5
Miles Sanders (PHI)|17|216.7
Alvin Kamara (NO)|15|211.7
Travis Etienne Jr. (JAC)|17|207.1
Kenneth Walker III (SEA)|15|202.5
James Conner (ARI)|13|200.2
Jerick McKinnon (KC)|17|196.3
D'Andre Swift (DET)|14|191.1
Ezekiel Elliott (DAL)|15|185.8
Devin Singletary (BUF)|17|178.2
David Montgomery (CHI)|16|177.7
Raheem Mostert (MIA)|16|168.3
AJ Dillon (GB)|17|167.6
Dameon Pierce (HOU)|13|166.4
Antonio Gibson (WAS)|15|165.9
Tyler Allgeier (ATL)|16|159.4
Jeff Wilson Jr. (MIA)|16|158.5
Cordarrelle Patterson (ATL)|13|154.7
Latavius Murray (DEN)|14|154.2
Jonathan Taylor (IND)|12|146.4
Samaje Perine (CIN)|16|142.1
Cam Akers (LAR)|15|141.3
Rachaad White (TB)|17|139.1
Isiah Pacheco (KC)|17|135.0
D'Onta Foreman (CAR)|16|131.0
Kareem Hunt (CLE)|17|126.8
Michael Carter (NYJ)|16|126.0
Khalil Herbert (CHI)|13|117.8
Breece Hall (NYJ)|7|115.1
Brian Robinson Jr. (WAS)|12|112.7
James Cook III (BUF)|17|107.5
Kenyan Drake (BAL)|12|104.1
Clyde Edwards-Helaire (KC)|10|98.3
Jaylen Warren (PIT)|16|93.3
Damien Harris (NE)|11|90.9
Eno Benjamin (NO)|13|89.6
James Robinson (NYJ)|11|88.6
Alexander Mattison (MIN)|17|88.4
Kenny Gainwell (PHI)|17|87.9
Chuba Hubbard (CAR)|14|87.7
Melvin Gordon III (DEN)|10|87.1
Deon Jackson (IND)|12|84.5
Nyheim Miller-Hines (BUF)|16|81.4
J.K. Dobbins (BAL)|8|81.2
Dontrell Hilliard (TEN)|12|77.2
Chase Edmonds (DEN)|13|74.2
Darrell Henderson Jr. (LAR)|10|73.5
Rex Burkhead (HOU)|15|71.3
JaMycal Hasty (JAC)|14|70.5
Joshua Kelley (LAC)|12|64.8
Zack Moss (IND)|13|64.5
Matt Breida (NYG)|17|59.8
Gus Edwards (BAL)|9|59.3
Bam Knight (NYJ)|7|59.0
J.D. McKissic (WAS)|9|55.8
Ameer Abdullah (LV)|16|54.1
Kyle Juszczyk (SF)|13|53.6
Rashaad Penny (SEA)|5|52.2
Justin Jackson (DET)|15|51.1
Mark Ingram II (NO)|10|50.1
Dare Ogunbowale (HOU)|15|48.7
DeeJay Dallas (SEA)|15|47.2"""

ACT_WR = """Justin Jefferson (MIN)|17|368.6
Tyreek Hill (MIA)|17|347.2
Davante Adams (LV)|17|335.5
Stefon Diggs (BUF)|17|321.2
CeeDee Lamb (DAL)|17|301.6
A.J. Brown (PHI)|17|299.6
Amon-Ra St. Brown (DET)|16|267.6
Jaylen Waddle (MIA)|17|259.2
DeVonta Smith (PHI)|17|254.6
Amari Cooper (CLE)|17|247.0
Ja'Marr Chase (CIN)|13|242.4
Christian Kirk (JAC)|17|241.9
Tyler Lockett (SEA)|16|237.3
Terry McLaurin (WAS)|17|229.0
Brandon Aiyuk (SF)|17|227.8
DK Metcalf (SEA)|17|226.8
Mike Evans (TB)|15|225.4
Tee Higgins (CIN)|15|223.2
Chris Godwin Jr. (TB)|15|222.8
Michael Pittman Jr. (IND)|16|216.5
Garrett Wilson (NYJ)|17|215.7
Jerry Jeudy (DEN)|15|204.2
Cooper Kupp (LAR)|9|201.4
DJ Moore (CAR)|17|199.1
Chris Olave (NO)|15|198.2
Zay Jones (JAC)|16|198.1
JuJu Smith-Schuster (KC)|16|185.3
Diontae Johnson (PIT)|17|180.7
Jakobi Meyers (NE)|14|180.3
Adam Thielen (MIN)|17|180.0
Drake London (ATL)|17|178.6
Mike Williams (LAC)|13|176.5
Curtis Samuel (WAS)|17|176.3
Tyler Boyd (CIN)|17|175.5
Allen Lazard (GB)|15|174.8
Gabe Davis (BUF)|15|171.6
Joshua Palmer (LAC)|16|169.3
Deebo Samuel Sr. (SF)|13|168.4
Donovan Peoples-Jones (CLE)|17|167.1
George Pickens (PIT)|17|166.5
Christian Watson (GB)|14|164.1
Keenan Allen (LAC)|10|164.0
Courtland Sutton (DEN)|15|159.4
Hollywood Brown (ARI)|12|156.0
K.J. Osborn (MIN)|17|155.6
Mack Hollins (LV)|17|154.2
DeAndre Hopkins (ARI)|9|151.7
Parris Campbell (IND)|17|149.1
Brandin Cooks (HOU)|13|145.6
Richie James Jr. (NYG)|16|132.5
Jahan Dotson (WAS)|12|130.6
Darius Slayton (NYG)|15|128.4
Russell Gage Jr. (TB)|13|123.6
Marquez Valdes-Scantling (KC)|17|122.4
Isaiah McKenzie (BUF)|16|119.8
Marvin Jones Jr. (JAC)|16|116.9
Kalif Raymond (DET)|17|116.2
Devin Duvernay (BAL)|14|116.1
Robert Woods (TEN)|17|115.7
Chris Moore (HOU)|15|115.1
Noah Brown (DAL)|16|114.5
Greg Dortch (ARI)|16|113.1
DeAndre Carter (LAC)|17|112.3
Alec Pierce (IND)|16|112.3
Olamide Zaccheaus (ATL)|17|110.0
Michael Gallup (DAL)|14|105.4
Chase Claypool (CHI)|15|105.0
Josh Reynolds (DET)|12|103.9
Demarcus Robinson (BAL)|16|103.8
DeVante Parker (NE)|13|102.9
Romeo Doubs (GB)|13|101.6
Darnell Mooney (CHI)|11|101.5
Rashid Shaheed (NO)|12|100.5
Isaiah Hodgins (NYG)|9|100.2
DJ Chark Jr. (DET)|11|98.2
Corey Davis (NYJ)|13|97.6
Nico Collins (HOU)|10|97.1
Treylon Burks (TEN)|11|94.1
Mecole Hardman Jr. (KC)|8|93.8
Marquise Goodwin (SEA)|13|90.2
Kendrick Bourne (NE)|16|88.3
Elijah Moore (NYJ)|16|88.1
Allen Robinson II (LAR)|10|84.9
Quez Watkins (PHI)|17|84.5
Ben Skowronek (LAR)|14|84.3
Trent Sherfield Sr. (MIA)|16|83.7
Terrace Marshall Jr. (CAR)|13|83.0
Nick Westbrook-Ikhine (TEN)|16|82.7
Jauan Jennings (SF)|16|82.6
Randall Cobb (GB)|13|81.7
Hunter Renfrow (LV)|10|79.0
Van Jefferson (LAR)|10|78.9"""

ACT_TE = """Travis Kelce (KC)|17|316.3
T.J. Hockenson (MIN)|17|215.4
George Kittle (SF)|15|200.5
Mark Andrews (BAL)|15|190.5
Evan Engram (JAC)|17|176.9
Tyler Higbee (LAR)|16|152.0
Pat Freiermuth (PIT)|15|148.2
Cole Kmet (CHI)|17|147.3
Taysom Hill (NO)|16|145.8
Dalton Schultz (DAL)|15|142.7
David Njoku (CLE)|14|142.0
Dallas Goedert (PHI)|12|141.2
Gerald Everett (LAC)|15|139.5
Dawson Knox (BUF)|15|135.7
Juwan Johnson (NO)|16|134.8
Tyler Conklin (NYJ)|17|131.5
Noah Fant (SEA)|17|122.6
Jordan Akins (HOU)|15|116.5
Zach Ertz (ARI)|10|115.6
Robert Tonyan (GB)|17|112.0
Hayden Hurst (CIN)|14|109.9
Hunter Henry (NE)|16|103.9
Mike Gesicki (MIA)|17|98.2
Austin Hooper (TEN)|17|97.4
Chig Okonkwo (TEN)|17|97.2
Cade Otton (TB)|16|93.1
Isaiah Likely (BAL)|15|91.3
Will Dissly (SEA)|15|86.9
Greg Dulcich (DEN)|10|86.1
Foster Moreau (LV)|14|85.2
Darren Waller (LV)|9|84.8
Logan Thomas (WAS)|13|77.3
Kyle Pitts Sr. (ATL)|10|75.6
Daniel Bellinger (NYG)|12|75.0
Jelani Woods (IND)|14|74.2
Noah Gray (KC)|17|70.0
Colby Parkinson (SEA)|14|69.2
Brock Wright (DET)|16|63.6
Harrison Bryant (CLE)|14|61.7
Trey McBride (ARI)|14|61.5
Kylen Granson (IND)|13|61.2
C.J. Uzomah (NYJ)|14|56.2"""

# ---------------- Games played: FantasyPros stats pages, G column ----------------
G20_QB = """Josh Allen|16
Kyler Murray|16
Aaron Rodgers|16
Patrick Mahomes II|15
Deshaun Watson|16
Russell Wilson|16
Ryan Tannehill|16
Tom Brady|16
Justin Herbert|15
Lamar Jackson|15
Kirk Cousins|16
Matt Ryan|16
Derek Carr|16
Ben Roethlisberger|15
Cam Newton|15
Matthew Stafford|16
Baker Mayfield|16
Jared Goff|15
Teddy Bridgewater|15
Philip Rivers|16
Drew Brees|12
Carson Wentz|12
Drew Lock|13
Daniel Jones|14
Joe Burrow|10
Gardner Minshew II|9
Mitchell Trubisky|10
Ryan Fitzpatrick|10
Sam Darnold|12
Andy Dalton|11
Tua Tagovailoa|10
Dak Prescott|5
Nick Mullens|10
Jalen Hurts|15
Nick Foles|9
Alex Smith|8
Jimmy Garoppolo|6
Mike Glennon|5
Joe Flacco|5
Brandon Allen|5
C.J. Beathard|6
Kyle Allen|4
Jake Luton|3
Jeff Driskel|3
Marcus Mariota|1
Chad Henne|3
Ryan Finley|5
Jacoby Brissett|11
Mason Rudolph|5
Colt McCoy|4
Jarrett Stidham|5
Garrett Gilbert|2
Brett Rypien|3
Blaine Gabbert|4
Chase Daniel|4
John Wolford|1
P.J. Walker|4
Taylor Heinicke|1
Matt Barkley|5
Trace McSorley|2
Tyrod Taylor|2
Chris Streveler|5
Ben DiNucci|3
Robert Griffin III|4
Brian Hoyer|1
Tyler Huntley|2
David Blough|1
Tommy Stevens|1
Jameis Winston|4"""

G20_RB = """Alvin Kamara|15
Dalvin Cook|14
Derrick Henry|16
David Montgomery|15
Aaron Jones Sr.|14
Jonathan Taylor|15
James Robinson|14
Josh Jacobs|15
Ezekiel Elliott|15
Kareem Hunt|16
Nick Chubb|12
Mike Davis|15
Antonio Gibson|14
Melvin Gordon III|15
Nyheim Miller-Hines|16
Kenyan Drake|15
J.D. McKissic|16
D'Andre Swift|13
Chris Carson|12
Ronald Jones II|14
David Johnson|12
Clyde Edwards-Helaire|13
Miles Sanders|12
J.K. Dobbins|15
Chase Edmonds|16
Austin Ekeler|10
James Conner|13
Myles Gaskin|10
Todd Gurley II|15
Giovani Bernard|16
Devin Singletary|16
Jeff Wilson Jr.|12
Wayne Gallman Jr.|15
Latavius Murray|15
Leonard Fournette|13
Darrell Henderson Jr.|15
Gus Edwards|16
Jamaal Williams|14
Jerick McKinnon|16
Adrian Peterson|16
Tony Pollard|16
James White|14
Malcolm Brown|16
Rex Burkhead|10
Cam Akers|12
Zack Moss|13
Frank Gore|15
Raheem Mostert|8
Joe Mixon|6
Boston Scott|16
Brian Hill|16
Kalen Ballage|11
Damien Harris|10
Christian McCaffrey|3
Alexander Mattison|13
Devontae Booker|16
Carlos Hyde|10
Duke Johnson Jr.|11
Kyle Juszczyk|16
Joshua Kelley|14
Sony Michel|9
Benny Snell Jr.|16
Le'Veon Bell|11
Kerryon Johnson|16
Salvon Ahmed|6
Phillip Lindsay|11
Samaje Perine|16
Justin Jackson|9
Ty Johnson|13
Jordan Wilkins|15
Ito Smith|14
Dion Lewis|16
DeeJay Dallas|12
Cordarrelle Patterson|16
Peyton Barber|16
Darrel Williams|16
Mark Ingram II|11
La'Mical Perine|10
Jalen Richard|13
Jeremy McNichols|16
Chris Thompson|8
Matt Breida|12
Alfred Morris|9
AJ Dillon|11
Royce Freeman|16
Josh Adams|8
Rodney Smith|7"""

G20_WR = """Davante Adams|14
Tyreek Hill|15
Stefon Diggs|16
DeAndre Hopkins|16
Calvin Ridley|15
Justin Jefferson|16
DK Metcalf|16
Tyler Lockett|16
Allen Robinson II|16
Adam Thielen|15
Mike Evans|16
A.J. Brown|14
Robert Woods|16
Keenan Allen|14
Amari Cooper|16
JuJu Smith-Schuster|16
Brandin Cooks|15
Marvin Jones Jr.|16
Robbie Anderson|16
Terry McLaurin|15
Diontae Johnson|15
CeeDee Lamb|16
Chase Claypool|16
Curtis Samuel|15
DJ Moore|15
Cooper Kupp|15
Cole Beasley|15
Tee Higgins|16
Tyler Boyd|15
Corey Davis|14
Chris Godwin|12
William Fuller V|11
Jarvis Landry|15
Nelson Agholor|16
Brandon Aiyuk|12
Hollywood Brown|16
Russell Gage Jr.|16
Michael Gallup|16
Jamison Crowder|12
DeVante Parker|14
Emmanuel Sanders|14
T.Y. Hilton|15
Sterling Shepard|12
Tim Patrick|15
Jerry Jeudy|16
Laviska Shenault Jr.|14
Keelan Cole Sr.|16
Mike Williams|15
DJ Chark Jr.|13
Darnell Mooney|16
Christian Kirk|14
Julio Jones|9
Jakobi Meyers|14
Darius Slayton|16
Marquez Valdes-Scantling|16
Zach Pascal|16
Gabe Davis|16
Greg Ward|16
Hunter Renfrow|16
Kendrick Bourne|15
Mecole Hardman Jr.|16
Josh Reynolds|16
Rashard Higgins|13
David Moore|16
Antonio Brown|8
Travis Fulgham|13
Damiere Byrd|16
A.J. Green|16
Anthony Miller|16
Demarcus Robinson|15
Danny Amendola|14
Tre'Quan Smith|14
Scotty Miller|16
Larry Fitzgerald|13
Randall Cobb|10
Isaiah McKenzie|16
James Washington|16
Breshad Perriman|12
Michael Pittman Jr.|13
Allen Lazard|10
Braxton Berrios|16
Chris Conley|15
Jalen Guyton|16
John Brown|9
Willie Snead IV|13
KJ Hamler|13
Sammy Watkins|10
Jakeem Grant Sr.|14
Jalen Reagor|11"""

G20_TE = """Travis Kelce|15
Darren Waller|16
Logan Thomas|16
Robert Tonyan|16
T.J. Hockenson|16
Mark Andrews|14
Mike Gesicki|15
Taysom Hill|16
Rob Gronkowski|16
Noah Fant|15
Hayden Hurst|16
Dalton Schultz|16
Hunter Henry|14
Jimmy Graham|16
Eric Ebron|15
Evan Engram|16
Jonnu Smith|15
Tyler Higbee|15
Jared Cook|15
George Kittle|8
Dallas Goedert|11
Austin Hooper|13
Irv Smith Jr.|13
Dan Arnold|16
Gerald Everett|16
Anthony Firkser|16
Jordan Akins|13
Trey Burton|13
Tyler Eifert|15
Mo Alie-Cox|15
Drew Sample|16
Zach Ertz|11
Darren Fells|16
Chris Herndon IV|16
Jordan Reed|10
Richard Rodgers|14
Cameron Brate|16
Dawson Knox|12
Jacob Hollister|16
Kyle Rudolph|12
Jack Doyle|14
Cole Kmet|16
Harrison Bryant|15
Will Dissly|16
Durham Smythe|15
James O'Shaughnessy|15
Greg Olsen|11
David Njoku|13
Ross Dwelley|16
Adam Shaheen|16
Tyler Conklin|16
Donald Parham Jr.|13
Pharaoh Brown|13
Tyler Kroft|10
Ian Thomas|16
Jesse James|16
Marcedes Lewis|15
Adam Trautman|15
O.J. Howard|4
Nick Boyle|9
Foster Moreau|16
Jason Witten|16
Ryan Izzo|12
Nick Vannett|15
Jace Sternberger|12
Kaden Smith|15
Albert Okwuegbunam Jr.|4"""

G21_QB = """Josh Allen|17
Justin Herbert|17
Tom Brady|17
Patrick Mahomes II|17
Matthew Stafford|17
Aaron Rodgers|16
Dak Prescott|16
Joe Burrow|16
Jalen Hurts|15
Kyler Murray|14
Kirk Cousins|16
Ryan Tannehill|17
Derek Carr|17
Carson Wentz|17
Lamar Jackson|12
Russell Wilson|14
Jimmy Garoppolo|15
Mac Jones|17
Taylor Heinicke|16
Matt Ryan|17
Ben Roethlisberger|16
Trevor Lawrence|17
Teddy Bridgewater|14
Jared Goff|14
Baker Mayfield|14
Tua Tagovailoa|13
Daniel Jones|11
Sam Darnold|12
Davis Mills|13
Zach Wilson|13
Justin Fields|12
Jameis Winston|7
Trevor Siemian|6
Andy Dalton|8
Cam Newton|8
Tyrod Taylor|6
Tyler Huntley|7
Jacoby Brissett|11
Trey Lance|6
Geno Smith|4
Drew Lock|6
Mike White|4
Josh Johnson|4
Colt McCoy|8
Mike Glennon|6
Gardner Minshew II|3
Tim Boyle|4
Case Keenum|5
Cooper Rush|4
Jordan Love|6
Joe Flacco|2
Mason Rudolph|2
P.J. Walker|5
Nick Foles|1
Marcus Mariota|7
Jake Fromm|3
Brandon Allen|5
Sean Mannion|1
Brian Hoyer|5
Nick Mullens|1
Mitchell Trubisky|5
Kyle Allen|2
Garrett Gilbert|1
Ian Book|1
Chad Henne|4
Chris Streveler|2
Blaine Gabbert|6
C.J. Beathard|2
Sam Ehlinger|3
Ryan Fitzpatrick|1
David Blough|1
Nathan Peterman|1"""

G21_RB = """Jonathan Taylor|17
Austin Ekeler|16
Najee Harris|17
Joe Mixon|16
James Conner|15
Leonard Fournette|14
Ezekiel Elliott|17
Alvin Kamara|13
Cordarrelle Patterson|16
Antonio Gibson|16
Aaron Jones Sr.|15
Josh Jacobs|15
Nick Chubb|14
Damien Harris|15
D'Andre Swift|13
Dalvin Cook|13
Javonte Williams|17
Devin Singletary|17
Darrel Williams|17
David Montgomery|14
Melvin Gordon III|16
Derrick Henry|8
AJ Dillon|17
James Robinson|14
Myles Gaskin|17
Elijah Mitchell|12
Darrell Henderson Jr.|12
Tony Pollard|15
Michael Carter|14
Saquon Barkley|14
Devonta Freeman|16
Sony Michel|17
Devontae Booker|16
Chase Edmonds|12
Mike Davis|17
Chuba Hubbard|16
J.D. McKissic|11
Christian McCaffrey|7
Alexander Mattison|16
Brandon Bolden|16
Kenny Gainwell|16
Rashaad Penny|10
Jamaal Williams|13
Clyde Edwards-Helaire|10
Miles Sanders|12
Ty Johnson|15
Rhamondre Stevenson|12
Nyheim Miller-Hines|17
Kareem Hunt|8
Mark Ingram II|14
Zack Moss|13
Rex Burkhead|15
D'Ernest Johnson|13
Latavius Murray|14
Kenyan Drake|12
Boston Scott|11
D'Onta Foreman|9
Ameer Abdullah|17
Justin Jackson|14
Samaje Perine|15
David Johnson|13
Ronald Jones II|15
Khalil Herbert|16
Kyle Juszczyk|15
Jeremy McNichols|13
Dontrell Hilliard|8
Alex Collins|11
Jordan Howard|7
Travis Homer|14
Damien Williams|12
DeeJay Dallas|17
Giovani Bernard|10
Duke Johnson Jr.|5
Derrick Gore|8
Jaret Patterson|15
Tevin Coleman|11
Jeff Wilson Jr.|9
Demetric Felton Jr.|15
Dare Ogunbowale|13
Peyton Barber|10
Chris Evans|9
JaMycal Hasty|11
Chris Carson|4
Carlos Hyde|12
Phillip Lindsay|14
Matt Breida|7
Ty'Son Williams|8
Salvon Ahmed|11
Le'Veon Bell|8
Ke'Shawn Vaughn|6
Jerick McKinnon|9
Elijhaa Penny|13"""

G21_WR = """Cooper Kupp|17
Davante Adams|16
Deebo Samuel Sr.|16
Justin Jefferson|17
Ja'Marr Chase|17
Tyreek Hill|17
Stefon Diggs|17
Diontae Johnson|16
Mike Evans|16
Hunter Renfrow|17
Keenan Allen|16
Mike Williams|16
Jaylen Waddle|16
DK Metcalf|17
Chris Godwin Jr.|14
Tyler Lockett|16
Michael Pittman Jr.|17
DJ Moore|17
CeeDee Lamb|16
Brandin Cooks|16
Amon-Ra St. Brown|16
Hollywood Brown|16
Darnell Mooney|17
Tee Higgins|14
Terry McLaurin|17
Christian Kirk|17
Amari Cooper|15
Adam Thielen|13
Jakobi Meyers|16
DeVonta Smith|17
Tyler Boyd|16
A.J. Brown|13
Kendrick Bourne|17
Marvin Jones Jr.|17
Brandon Aiyuk|17
Van Jefferson|17
Chase Claypool|15
Russell Gage Jr.|13
Cole Beasley|16
K.J. Osborn|17
A.J. Green|16
Tim Patrick|16
Marquez Callaway|17
Courtland Sutton|17
Cedrick Wilson Jr.|14
DeAndre Hopkins|10
Allen Lazard|14
Mecole Hardman Jr.|17
Robbie Chosen|17
Elijah Moore|11
Robert Woods|9
Jarvis Landry|12
Kalif Raymond|16
Emmanuel Sanders|14
Odell Beckham Jr.|14
Laviska Shenault Jr.|16
Byron Pringle|16
Gabe Davis|15
Antonio Brown|7
Braxton Berrios|16
Quez Watkins|17
Deonte Harty|13
Jamison Crowder|12
Donovan Peoples-Jones|14
Bryan Edwards|16
Nick Westbrook-Ikhine|15
Zay Jones|15
Corey Davis|9
DeVante Parker|10
Rashod Bateman|12
Nelson Agholor|15
Jalen Guyton|16
Zach Pascal|16
Randall Cobb|11
Joshua Palmer|15
Michael Gallup|9
Olamide Zaccheaus|15
Kenny Golladay|14
Tre'Quan Smith|10
Allen Robinson II|12
Marquez Valdes-Scantling|11
DeAndre Carter|17
Freddie Swain|17
Jerry Jeudy|10
Henry Ruggs III|7
Nico Collins|14
Devin Duvernay|16
Laquon Treadwell|12
Kadarius Toney|9
Jauan Jennings|13"""

G21_TE = """Mark Andrews|17
Travis Kelce|16
Dalton Schultz|17
George Kittle|14
Zach Ertz|17
Kyle Pitts Sr.|17
Rob Gronkowski|12
Dallas Goedert|15
Mike Gesicki|17
Hunter Henry|16
Dawson Knox|15
Noah Fant|16
Pat Freiermuth|16
Tyler Higbee|15
T.J. Hockenson|12
Tyler Conklin|17
Darren Waller|11
Jared Cook|16
C.J. Uzomah|16
Taysom Hill|12
Cole Kmet|17
Gerald Everett|15
David Njoku|15
Evan Engram|15
Austin Hooper|15
Foster Moreau|15
Mo Alie-Cox|17
Jack Doyle|15
Anthony Firkser|15
Cameron Brate|16
Albert Okwuegbunam Jr.|14
Dan Arnold|11
Geoff Swaim|16
Durham Smythe|16
Ricky Seals-Jones|11
Jonnu Smith|16
Ryan Griffin|14
Hayden Hurst|12
Adam Trautman|11
Harrison Bryant|15
Josiah Deguara|14
Kyle Rudolph|15
Donald Parham Jr.|14
Brevin Jordan|8
Logan Thomas|5
Tommy Tremble|15
Juwan Johnson|13
John Bates|13
Jimmy Graham|11
James O'Shaughnessy|7
Robert Tonyan|8
Will Dissly|13
MyCole Pruitt|13
Marcedes Lewis|13
Jordan Akins|12
Maxx Williams|5
Tyler Kroft|9
Stephen Anderson|14
Pharaoh Brown|13
Ian Thomas|14
Zach Gentry|10
Brock Wright|8
O.J. Howard|11
Blake Jarwin|8
Eric Ebron|8
Nick Vannett|7
Adam Shaheen|9
Jody Fortson Jr.|4"""


def lines(block):
    return [l.strip() for l in block.strip().split("\n") if l.strip()]


# ADP: drop DEF/PK
adp = []
for l in lines(ADP_RAW):
    _, name, pos, team, val = l.split("|")
    if pos in ("DEF", "PK"):
        continue
    adp.append({"name": name, "pos": pos, "team": team, "adp": float(val)})

# Projections
proj = []
for l in lines(PROJ_QB):
    name, team, fpts = l.split("|")
    proj.append({"name": name, "pos": "QB", "proj": float(fpts)})
for block, pos in ((PROJ_RB, "RB"), (PROJ_WR, "WR"), (PROJ_TE, "TE")):
    for l in lines(block):
        name, team, rec, fpts = l.split("|")
        ppr = round(float(fpts) + 0.5 * int(rec), 1)
        proj.append({"name": name, "pos": pos, "proj": ppr})

# Actuals
actual = []
for block, pos in ((ACT_QB, "QB"), (ACT_RB, "RB"), (ACT_WR, "WR"), (ACT_TE, "TE")):
    for l in lines(block):
        nm, g, pts = l.split("|")
        name = nm.rsplit(" (", 1)[0]
        actual.append({"name": name, "pos": pos, "pts": float(pts), "games": int(g)})

# Games
def games(block, pos):
    out = []
    for l in lines(block):
        name, g = l.split("|")
        out.append([name, pos, int(g)])
    return out

games2020 = games(G20_QB, "QB") + games(G20_RB, "RB") + games(G20_WR, "WR") + games(G20_TE, "TE")
games2021 = games(G21_QB, "QB") + games(G21_RB, "RB") + games(G21_WR, "WR") + games(G21_TE, "TE")

notes = (
    "Collected 2026-08-16 via WebFetch, numbers transcribed as displayed (nothing imputed). "
    "adp2022: FantasyFootballCalculator PPR 12-team 2022 archive (mock drafts Sep 3-4 2022, 1,633 drafts); 'adp' = the Overall avg-pick column. "
    "The archived table only has 157 rows total incl. 6 DEF + 5 PK, so after dropping K/DST there are 146 skill players (not 200); deepest ADP = 153.8. "
    "FFC name quirks kept verbatim (e.g. 'Aaron Jones Sr.', 'Hollywood Brown', 'Kyle Pitts Sr.', 'Brian Robinson'). "
    "proj2022: FFToday 2022 preseason projections (playerproj.php PosID 10/20/30/40, default league). Page legend says 'FFToday Half-PPR Scoring'; "
    "verified by recomputation (Jonathan Taylor 1568+321 yds, 16 TD, 39 rec -> 284.9 std + 0.5*39 = 304.4 = listed FPts; McCaffrey matches too). "
    "So PPR proj = listed FPts + 0.5*Receptions for RB/WR/TE (NOT +1.0*Rec, since FPts already includes 0.5/rec); QB proj = listed FPts unchanged (no receptions). "
    "32 QB, 94 RB, 100 WR, 32 TE. FFToday name forms kept ('Aaron Jones', 'Travis Etienne', 'Robbie Chosen' = Robby Anderson, 'Melvin Gordon' listed on DEN preseason). "
    "actual2022: FantasyPros /nfl/stats/{qb,rb,wr,te}.php?year=2022&scoring=PPR, FPTS and G columns quoted verbatim (38 QB, 75 RB, 92 WR, 42 TE). "
    "FantasyPros QB scoring = 4 pts/pass TD. CAVEAT: FantasyPros lists G=17 for Josh Allen and Joe Burrow (verified by verbatim row transcription; their FPTS/G column = FPTS/17), "
    "although BUF and CIN actually played only 16 games in 2022 (Week 17 BUF@CIN cancelled after Hamlin injury) - treat those two G values as 16 if physical games matter. "
    "Taysom Hill appears as TE (FantasyPros classification). "
    "games2020/games2021: same FantasyPros stats pages for year=2020 (16-game season) and 2021 (17-game season), G column, top-of-table order; "
    "2020: 69 QB / 87 RB / 89 WR / 67 TE; 2021: 72 QB / 92 RB / 90 WR / 68 TE. "
    "Names are NOT normalized across sources - joiners must handle suffix/alias variants (e.g. FFC 'Nyheim Hines' vs FantasyPros 'Nyheim Miller-Hines', "
    "'Patrick Mahomes' vs 'Patrick Mahomes II', 'DJ Moore' vs 'D.J. Moore', 'Robbie Chosen'/'Robbie Anderson', 'Chris Godwin' vs 'Chris Godwin Jr.'). "
    "K/DST excluded everywhere."
)

out = {
    "adp2022": adp,
    "proj2022": proj,
    "actual2022": actual,
    "games2020": games2020,
    "games2021": games2021,
    "notes": notes,
}

with open("/home/claude/work/data2/oos2022.json", "w") as f:
    json.dump(out, f, indent=1)

print("adp2022:", len(adp))
from collections import Counter
print(" adp by pos:", dict(Counter(p["pos"] for p in adp)))
print("proj2022:", len(proj), dict(Counter(p["pos"] for p in proj)))
print("actual2022:", len(actual), dict(Counter(p["pos"] for p in actual)))
print("games2020:", len(games2020), dict(Counter(g[1] for g in games2020)))
print("games2021:", len(games2021), dict(Counter(g[1] for g in games2021)))
# sanity checks
names = [p["name"] for p in adp]
assert len(names) == len(set(names)), "dup in adp"
spot = {p["name"]: p["proj"] for p in proj}
assert spot["Jonathan Taylor"] == 323.9 and spot["Cooper Kupp"] == 324.3 and spot["Mark Andrews"] == 246.4
print("spot-checks ok")

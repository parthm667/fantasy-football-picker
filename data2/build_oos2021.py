import json

# ---------------- ADP: FantasyFootballCalculator PPR 12-team 2021 (preseason) ----------------
adp_rows = [
("Christian McCaffrey","RB","CAR",1.2),("Dalvin Cook","RB","MIN",2.5),("Alvin Kamara","RB","NO",3.8),
("Derrick Henry","RB","TEN",4.0),("Ezekiel Elliott","RB","DAL",5.3),("Davante Adams","WR","GB",6.4),
("Aaron Jones Sr.","RB","GB",7.5),("Travis Kelce","TE","KC",8.2),("Austin Ekeler","RB","LAC",8.5),
("Nick Chubb","RB","CLE",9.9),("Tyreek Hill","WR","KC",10.6),("Saquon Barkley","RB","NYG",12.0),
("Najee Harris","RB","PIT",12.9),("Stefon Diggs","WR","BUF",13.5),("Jonathan Taylor","RB","IND",13.8),
("Antonio Gibson","RB","WAS",15.6),("DeAndre Hopkins","WR","ARI",17.0),("Calvin Ridley","WR","ATL",18.0),
("Joe Mixon","RB","CIN",19.2),("DK Metcalf","WR","SEA",19.7),("Clyde Edwards-Helaire","RB","KC",20.4),
("Darren Waller","TE","LV",21.5),("Justin Jefferson","WR","MIN",22.4),("Patrick Mahomes","QB","KC",22.9),
("A.J. Brown","WR","TEN",24.8),("David Montgomery","RB","CHI",25.9),("Keenan Allen","WR","LAC",25.9),
("Chris Carson","RB","SEA",28.0),("George Kittle","TE","SF",28.5),("James Robinson","RB","JAX",29.1),
("CeeDee Lamb","WR","DAL",29.6),("Terry McLaurin","WR","WAS",30.3),("Allen Robinson II","WR","CHI",32.7),
("D'Andre Swift","RB","DET",34.0),("Josh Allen","QB","BUF",34.4),("Robert Woods","WR","LAR",35.1),
("Josh Jacobs","RB","LV",35.4),("Mike Evans","WR","TB",37.8),("Miles Sanders","RB","PHI",38.7),
("Amari Cooper","WR","DAL",40.0),("Kyle Pitts Sr.","TE","ATL",40.3),("Kyler Murray","QB","ARI",41.3),
("Cooper Kupp","WR","LAR",41.3),("Mike Davis","RB","ATL",43.1),("Darrell Henderson Jr.","RB","LAR",43.8),
("Diontae Johnson","WR","PIT",44.9),("Myles Gaskin","RB","MIA",45.7),("Julio Jones","WR","TEN",46.0),
("Chris Godwin Jr.","WR","TB",47.2),("Tyler Lockett","WR","SEA",48.4),("Lamar Jackson","QB","BAL",50.9),
("Adam Thielen","WR","MIN",52.3),("Javonte Williams","RB","DEN",52.7),("Mark Andrews","TE","BAL",52.8),
("Kareem Hunt","RB","CLE",53.2),("Brandon Aiyuk","WR","SF",53.9),("T.J. Hockenson","TE","DET",55.4),
("Damien Harris","RB","NE",55.5),("Gus Edwards","RB","BAL",56.6),("DJ Moore","WR","CAR",57.0),
("Aaron Rodgers","QB","GB",59.0),("Chase Edmonds","RB","ARI",60.4),("Chase Claypool","WR","PIT",61.1),
("Tee Higgins","WR","CIN",61.3),("Raheem Mostert","RB","SF",63.0),("Jerry Jeudy","WR","DEN",64.1),
("Dak Prescott","QB","DAL",66.7),("Trey Sermon","RB","SF",67.7),("Odell Beckham Jr.","WR","LAR",69.0),
("Justin Herbert","QB","LAC",69.3),("Russell Wilson","QB","SEA",69.4),("Michael Thomas","WR","NO",69.5),
("Logan Thomas","TE","WAS",72.2),("Antonio Brown","WR","TB",72.7),("Robbie Chosen","WR","CAR",75.0),
("Melvin Gordon III","RB","DEN",75.2),("Michael Carter","RB","NYJ",76.1),("Ja'Marr Chase","WR","CIN",77.4),
("DeVonta Smith","WR","PHI",77.6),("Tom Brady","QB","TB",77.8),("AJ Dillon","RB","GB",79.1),
("Noah Fant","TE","DEN",79.2),("Ronald Jones","RB","TB",79.8),("JuJu Smith-Schuster","WR","PIT",82.5),
("Kenny Golladay","WR","NYG",82.8),("Zack Moss","RB","BUF",83.8),("Matthew Stafford","QB","LAR",85.0),
("Courtland Sutton","WR","DEN",85.7),("Laviska Shenault Jr.","WR","JAX",85.9),("Robert Tonyan","TE","GB",87.2),
("Corey Davis","WR","NYJ",89.6),("Deebo Samuel Sr.","WR","SF",89.8),("Leonard Fournette","RB","TB",90.1),
("Marquez Callaway","WR","NO",90.5),("Devin Singletary","RB","BUF",91.2),("Jamaal Williams","RB","DET",92.0),
("Sony Michel","RB","LAR",93.4),("Dallas Goedert","TE","PHI",93.9),("Tyler Higbee","TE","LAR",95.8),
("Ryan Tannehill","QB","TEN",96.1),
("James Conner","RB","ARI",96.2),("Tyler Boyd","WR","CIN",97.3),("Jaylen Waddle","WR","MIA",99.2),
("Mecole Hardman Jr.","WR","KC",100.0),("Jalen Hurts","QB","PHI",100.2),("Tony Pollard","RB","DAL",102.7),
("Brandin Cooks","WR","HOU",102.9),("Kenyan Drake","RB","LV",102.9),("Michael Pittman Jr.","WR","IND",104.4),
("Alexander Mattison","RB","MIN",106.5),("Phillip Lindsay","RB","MIA",107.5),("Darnell Mooney","WR","CHI",109.0),
("Joe Burrow","QB","CIN",112.4),("DJ Chark","WR","JAX",112.8),("Jakobi Meyers","WR","NE",116.2),
("Mike Williams","WR","LAC",116.2),("J.D. McKissic","RB","WAS",116.8),("Jarvis Landry","WR","CLE",118.2),
("Trey Lance","QB","SF",118.2),("Nyheim Hines","RB","IND",120.6),("Giovani Bernard","RB","TB",120.9),
("Rhamondre Stevenson","RB","NE",121.3),("Justin Fields","QB","CHI",125.6),("Marvin Jones Jr.","WR","JAX",126.0),
("Chuba Hubbard","RB","CAR",127.6),("James White","RB","NE",128.8),("Will Fuller","WR","MIA",129.2),
("Matt Ryan","QB","ATL",129.8),("Latavius Murray","RB","BAL",130.6),("Jonnu Smith","TE","NE",130.7),
("Elijah Moore","WR","NYJ",132.6),("Russell Gage Jr.","WR","ATL",133.8),("Baker Mayfield","QB","CLE",134.3),
("Michael Gallup","WR","DAL",135.4),("Jameis Winston","QB","NO",137.3),("Rashaad Penny","RB","SEA",137.9),
("Tevin Coleman","RB","NYJ",139.0),("Curtis Samuel","WR","WAS",140.2),("Hollywood Brown","WR","BAL",140.9),
("Rob Gronkowski","TE","TB",142.8),("Ben Roethlisberger","QB","PIT",143.2),("Trevor Lawrence","QB","JAX",144.7),
("Damien Williams","RB","CHI",146.0),("Rondale Moore","WR","ARI",146.4),("Terrace Marshall Jr.","WR","CAR",149.0),
("Zach Wilson","QB","NYJ",149.1),("Hunter Henry","TE","NE",149.7),("Darrel Williams","RB","KC",150.3),
("Evan Engram","TE","NYG",150.9),("Cole Beasley","WR","BUF",150.9),("Adam Trautman","TE","NO",151.9),
("Mark Ingram II","RB","NO",154.2),("Justin Jackson","RB","LAC",154.6),("Kenny Gainwell","RB","PHI",154.8),
("Jared Cook","TE","LAC",155.0),("Devontae Booker","RB","NYG",155.5),("A.J. Green","WR","ARI",156.6),
("Gerald Everett","TE","SEA",156.6),("Zach Ertz","TE","ARI",157.1),("Pat Freiermuth","TE","PIT",157.3),
("Mac Jones","QB","NE",157.4),("Amon-Ra St. Brown","WR","DET",158.5),("Tony Jones","RB","NO",158.8),
("Marlon Mack","RB","IND",158.8),("Randall Cobb","WR","GB",159.7),("Jerick McKinnon","RB","KC",159.7),
("Tyrell Williams","WR","DET",160.0),("Tua Tagovailoa","QB","MIA",160.6),("Kirk Cousins","QB","MIN",160.9),
("Malcolm Brown","RB","MIA",161.7),("DeVante Parker","WR","MIA",162.3),("Ryan Fitzpatrick","QB","WAS",163.3),
("Deshaun Watson","QB","HOU",163.6),("Carson Wentz","QB","IND",167.1),("Nelson Agholor","WR","NE",170.7),
("Marquez Valdes-Scantling","WR","GB",170.9),("Carlos Hyde","RB","JAX",172.7),
]

# ---------------- Projections: FFToday 2021 preseason ----------------
# QB: FPts used as-is (no receptions). Verified formula: 0.04/pass yd + 4/pass TD + 0.1/rush yd + 6/rush TD, no INT penalty.
proj_qb = [
("Josh Allen","BUF",395.6),("Patrick Mahomes","KC",393.8),("Russell Wilson","SEA",378.8),
("Kyler Murray","ARI",377.1),("Lamar Jackson","BAL",373.3),("Dak Prescott","DAL",358.3),
("Aaron Rodgers","GB",356.3),("Tom Brady","TB",343.1),("Justin Herbert","LAC",336.0),
("Jalen Hurts","PHI",331.2),("Ryan Tannehill","TEN",318.1),("Joe Burrow","CIN",307.6),
("Kirk Cousins","MIN",304.4),("Trevor Lawrence","JAC",294.2),("Matthew Stafford","LAR",289.9),
("Matt Ryan","ATL",286.5),("Daniel Jones","NYG",285.7),("Derek Carr","LV",285.6),
("Sam Darnold","CAR",285.5),("Baker Mayfield","CLE",279.3),("Ryan Fitzpatrick","WAS",278.0),
("Ben Roethlisberger","PIT",277.8),("Tua Tagovailoa","MIA",269.7),("Zach Wilson","NYJ",262.7),
("Mac Jones","NE",258.0),("Carson Wentz","IND",243.5),("Justin Fields","CHI",240.6),
("Jameis Winston","NO",238.7),("Jared Goff","DET",235.9),("Teddy Bridgewater","DEN",200.6),
("Trey Lance","SF",179.1),("Tyrod Taylor","HOU",172.7),
]
# RB/WR/TE: (name, team, Rec, FPts_halfPPR). PPR = FPts + 0.5*Rec (FFToday default FPts verified = standard + 0.5/rec).
proj_rb = [
("Christian McCaffrey","CAR",89,337.0),("Dalvin Cook","MIN",46,291.1),("Derrick Henry","TEN",21,282.9),
("Alvin Kamara","NO",80,261.8),("Ezekiel Elliott","DAL",50,244.0),("Joe Mixon","CIN",48,238.4),
("Aaron Jones","GB",44,235.9),("Jonathan Taylor","IND",42,235.0),("Saquon Barkley","NYG",50,232.8),
("Antonio Gibson","WAS",48,223.6),("Najee Harris","PIT",42,221.7),("Austin Ekeler","LAC",75,220.7),
("Nick Chubb","CLE",29,212.8),("Chris Carson","SEA",43,207.3),("Clyde Edwards-Helaire","KC",48,200.3),
("Josh Jacobs","LV",31,200.1),("Chase Edmonds","ARI",61,191.5),("D'Andre Swift","DET",49,189.9),
("David Montgomery","CHI",40,188.7),("James Robinson","JAC",47,187.2),("Gus Edwards","BAL",24,186.0),
("Mike Davis","ATL",51,178.7),("Darrell Henderson","LAR",35,171.3),("Miles Sanders","PHI",34,169.6),
("Myles Gaskin","MIA",48,168.4),("Kareem Hunt","CLE",39,165.7),("Zack Moss","BUF",34,161.4),
("Damien Harris","NE",16,152.2),("Raheem Mostert","SF",27,148.3),("Javonte Williams","DEN",17,136.4),
("J.D. McKissic","WAS",72,130.3),("David Johnson","HOU",37,129.9),("Kenyan Drake","LV",45,129.8),
("Michael Carter","NYJ",31,126.6),("Ronald Jones","TB",18,126.2),("Leonard Fournette","TB",21,124.1),
("Jamaal Williams","DET",35,122.9),("Phillip Lindsay","HOU",26,119.9),("Tony Pollard","DAL",31,119.0),
("Melvin Gordon","DEN",20,117.8),("Sony Michel","LAR",14,117.2),("Trey Sermon","SF",21,114.2),
("Nyheim Hines","IND",50,113.7),("Devin Singletary","BUF",27,109.8),("James Conner","ARI",17,108.8),
("James White","NE",55,106.0),("Tevin Coleman","NYJ",20,102.0),("AJ Dillon","GB",15,98.2),
("Damien Williams","CHI",26,91.4),("Malcolm Brown","MIA",10,87.6),
("Alexander Mattison","MIN",18,83.3),("Ty Johnson","NYJ",23,79.9),("Rashaad Penny","SEA",14,78.3),
("Ty'Son Williams","BAL",12,77.7),("Darrel Williams","KC",27,77.5),("Latavius Murray","NO",20,76.9),
("Justin Jackson","LAC",18,73.1),("Rhamondre Stevenson","NE",14,72.4),("Giovani Bernard","TB",43,71.0),
("Carlos Hyde","JAC",18,69.8),
]
proj_wr = [
("Davante Adams","GB",123,276.4),("Tyreek Hill","KC",93,262.7),("Calvin Ridley","ATL",99,245.7),
("DeAndre Hopkins","ARI",112,238.6),("Stefon Diggs","BUF",100,232.3),("DK Metcalf","SEA",81,225.1),
("Justin Jefferson","MIN",91,223.0),("Keenan Allen","LAC",113,216.7),("A.J. Brown","TEN",80,209.6),
("Mike Evans","TB",77,205.8),("Allen Robinson","CHI",95,200.9),("Robert Woods","LAR",92,199.1),
("Tyler Lockett","SEA",91,198.1),("Amari Cooper","DAL",84,196.1),("Terry McLaurin","WAS",86,194.2),
("Adam Thielen","MIN",76,193.3),("CeeDee Lamb","DAL",80,189.6),("Diontae Johnson","PIT",88,187.5),
("Cooper Kupp","LAR",80,185.6),("Chris Godwin","TB",72,180.5),("Odell Beckham Jr.","CLE",76,180.0),
("Tee Higgins","CIN",78,179.5),("D.J. Moore","CAR",76,176.8),("Jerry Jeudy","DEN",74,176.5),
("JuJu Smith-Schuster","PIT",80,173.8),("Brandin Cooks","HOU",76,170.0),("Julio Jones","TEN",69,168.6),
("Brandon Aiyuk","SF",65,165.6),("Robbie Chosen","CAR",75,165.2),("Tyler Boyd","CIN",81,164.4),
("Laviska Shenault","JAC",77,164.1),("Deebo Samuel","SF",69,157.1),("Marvin Jones","JAC",64,154.6),
("Michael Gallup","DAL",60,153.5),("DeVante Parker","MIA",64,149.5),("Marquise Brown","BAL",59,149.2),
("Courtland Sutton","DEN",62,148.9),("Kenny Golladay","NYG",59,148.6),("Ja'Marr Chase","CIN",63,148.0),
("Michael Pittman Jr.","IND",62,144.6),("Henry Ruggs III","LV",56,144.1),("Jarvis Landry","CLE",68,140.8),
("Corey Davis","NYJ",64,140.1),("Chase Claypool","PIT",54,139.5),("Tyrell Williams","DET",60,139.5),
("Mike Williams","LAC",50,138.5),("DeVonta Smith","PHI",58,137.4),("Michael Thomas","NO",63,133.8),
("Mecole Hardman","KC",52,131.5),("Curtis Samuel","WAS",51,125.4),
("D.J. Chark","JAC",55,125.2),("Marquez Callaway","NO",50,122.5),("Nelson Agholor","NE",52,121.7),
("Darnell Mooney","CHI",56,121.2),("Jakobi Meyers","NE",53,119.3),("Cole Beasley","BUF",54,114.5),
("Bryan Edwards","LV",48,112.7),("Will Fuller","MIA",48,112.6),("T.Y. Hilton","IND",47,109.0),
("Elijah Moore","NYJ",54,108.6),("Russell Gage","ATL",51,107.2),("Emmanuel Sanders","BUF",44,106.9),
("Jalen Reagor","PHI",47,106.4),("A.J. Green","ARI",49,106.2),("Sterling Shepard","NYG",50,105.3),
("Antonio Brown","TB",46,105.1),("Jaylen Waddle","MIA",41,98.0),("Darius Slayton","NYG",41,94.0),
("Rondale Moore","ARI",48,93.3),("Jamison Crowder","NYJ",46,92.7),
]
proj_te = [
("Travis Kelce","KC",95,217.5),("Darren Waller","LV",103,215.2),("George Kittle","SF",89,190.4),
("Mark Andrews","BAL",66,156.6),("Kyle Pitts","ATL",65,149.2),("T.J. Hockenson","DET",72,144.7),
("Tyler Higbee","LAR",65,144.2),("Robert Tonyan","GB",63,135.0),("Logan Thomas","WAS",70,134.5),
("Dallas Goedert","PHI",60,119.5),("Noah Fant","DEN",59,119.0),("Mike Gesicki","MIA",51,117.2),
("Evan Engram","NYG",58,113.8),("Jared Cook","LAC",51,113.6),("Jonnu Smith","NE",57,111.3),
("Rob Gronkowski","TB",44,109.3),("Blake Jarwin","DAL",50,102.5),("Eric Ebron","PIT",51,100.9),
("Anthony Firkser","TEN",50,100.5),("Hunter Henry","NE",51,100.0),("Gerald Everett","SEA",46,99.6),
("Austin Hooper","CLE",48,94.6),("Jordan Akins","HOU",49,90.0),("Zach Ertz","PHI",40,85.7),
("C.J. Uzomah","CIN",42,81.5),("Tyler Conklin","MIN",40,79.5),("Adam Trautman","NO",37,75.1),
("Will Dissly","SEA",38,74.9),("Dawson Knox","BUF",33,74.1),("Cole Kmet","CHI",38,68.7),
("Jack Doyle","IND",32,68.4),("Mo Alie-Cox","IND",34,67.2),("Juwan Johnson","NO",35,65.9),
("Tyler Kroft","NYJ",30,61.6),("David Njoku","CLE",29,61.3),("Jimmy Graham","CHI",27,60.3),
("Hayden Hurst","ATL",29,57.1),("Geoff Swaim","TEN",30,55.8),("Brevin Jordan","HOU",30,55.6),
("Nick Boyle","BAL",28,52.6),
]

# ---------------- Actuals: FantasyPros 2021 PPR season totals ----------------
act_qb = [
("Josh Allen",17,417.7),("Justin Herbert",17,395.6),("Tom Brady",17,386.7),("Patrick Mahomes II",17,374.6),
("Matthew Stafford",17,346.8),("Aaron Rodgers",16,337.3),("Dak Prescott",16,330.4),("Joe Burrow",16,328.1),
("Jalen Hurts",15,321.2),("Kyler Murray",14,309.8),("Kirk Cousins",16,307.3),("Ryan Tannehill",17,282.3),
("Derek Carr",17,270.6),("Carson Wentz",17,264.9),("Lamar Jackson",12,253.0),("Russell Wilson",14,248.7),
("Jimmy Garoppolo",15,241.5),("Mac Jones",17,238.0),("Taylor Heinicke",16,237.7),("Matt Ryan",17,234.8),
("Ben Roethlisberger",16,228.0),("Trevor Lawrence",17,216.0),("Teddy Bridgewater",14,209.8),("Jared Goff",14,202.4),
("Baker Mayfield",14,195.8),("Tua Tagovailoa",13,190.9),("Daniel Jones",11,173.5),("Sam Darnold",12,170.5),
("Davis Mills",13,167.0),("Zach Wilson",13,162.9),("Justin Fields",12,136.9),("Jameis Winston",7,120.3),
("Trevor Siemian",6,93.2),("Andy Dalton",8,93.1),("Cam Newton",8,91.6),("Tyrod Taylor",6,86.9),
("Tyler Huntley",7,86.7),("Jacoby Brissett",11,76.4),
]
act_rb = [
("Jonathan Taylor",17,373.1),("Austin Ekeler",16,343.8),("Najee Harris",17,300.7),("Joe Mixon",16,287.9),
("James Conner",15,257.7),("Leonard Fournette",14,255.6),("Ezekiel Elliott",17,252.1),("Alvin Kamara",13,234.7),
("Cordarrelle Patterson",16,234.6),("Antonio Gibson",16,229.1),("Aaron Jones Sr.",15,229.0),("Josh Jacobs",15,226.0),
("Nick Chubb",14,215.3),("Damien Harris",15,210.1),("D'Andre Swift",13,208.9),("Dalvin Cook",13,206.3),
("Javonte Williams",17,204.9),("Devin Singletary",17,197.8),("Darrel Williams",17,196.0),("David Montgomery",14,196.0),
("Melvin Gordon III",16,195.1),("Derrick Henry",8,193.3),("AJ Dillon",17,185.6),("James Robinson",14,173.9),
("Myles Gaskin",17,173.6),("Elijah Mitchell",12,165.0),("Darrell Henderson Jr.",12,163.4),("Tony Pollard",15,162.6),
("Michael Carter",14,154.4),("Saquon Barkley",14,148.6),("Devonta Freeman",16,146.6),("Sony Michel",17,146.3),
("Devontae Booker",16,144.1),("Chase Edmonds",12,143.3),("Mike Davis",17,138.2),("Chuba Hubbard",16,137.6),
("J.D. McKissic",11,127.9),("Christian McCaffrey",7,127.5),("Alexander Mattison",16,125.9),("Brandon Bolden",16,124.1),
("Kenny Gainwell",16,123.4),("Rashaad Penny",10,121.7),("Jamaal Williams",13,119.8),("Clyde Edwards-Helaire",10,117.6),
("Miles Sanders",12,117.2),("Ty Johnson",15,117.0),("Rhamondre Stevenson",12,114.9),("Nyheim Miller-Hines",17,112.6),
("Kareem Hunt",8,110.0),("Mark Ingram II",14,108.6),("Zack Moss",13,105.2),("Rex Burkhead",15,104.3),
("D'Ernest Johnson",13,104.1),("Latavius Murray",14,103.6),("Kenyan Drake",12,102.5),("Boston Scott",11,98.6),
("D'Onta Foreman",9,93.9),("Ameer Abdullah",17,89.5),("Justin Jackson",14,86.2),("Samaje Perine",15,83.2),
("David Johnson",13,81.3),("Ronald Jones II",15,79.2),("Khalil Herbert",16,78.9),("Kyle Juszczyk",15,73.8),
("Jeremy McNichols",13,73.6),("Dontrell Hilliard",8,72.7),("Alex Collins",11,68.8),("Jordan Howard",7,62.5),
("Travis Homer",14,61.8),("Damien Williams",12,60.7),("DeeJay Dallas",17,60.1),("Giovani Bernard",10,59.1),
("Duke Johnson Jr.",5,59.1),("Derrick Gore",8,56.1),("Jaret Patterson",15,55.9),
]
act_wr = [
("Cooper Kupp",17,439.5),("Davante Adams",16,344.3),("Deebo Samuel Sr.",16,339.0),("Justin Jefferson",17,330.4),
("Ja'Marr Chase",17,304.6),("Tyreek Hill",17,296.5),("Stefon Diggs",17,285.5),("Diontae Johnson",16,274.4),
("Mike Evans",16,262.5),("Hunter Renfrow",17,259.1),("Keenan Allen",16,257.8),("Mike Williams",16,246.6),
("Jaylen Waddle",16,245.8),("DK Metcalf",17,244.3),("Chris Godwin Jr.",14,242.4),("Tyler Lockett",16,241.4),
("Michael Pittman Jr.",17,238.6),("DJ Moore",17,237.5),("CeeDee Lamb",16,232.8),("Brandin Cooks",16,231.8),
("Amon-Ra St. Brown",16,227.3),("Hollywood Brown",16,226.3),("Darnell Mooney",17,219.7),("Tee Higgins",14,219.1),
("Terry McLaurin",17,213.5),("Christian Kirk",17,207.6),("Amari Cooper",15,202.5),("Adam Thielen",13,199.8),
("Jakobi Meyers",16,186.3),("DeVonta Smith",17,185.6),("Tyler Boyd",16,183.8),("A.J. Brown",13,180.9),
("Kendrick Bourne",17,180.5),("Marvin Jones Jr.",17,180.2),("Brandon Aiyuk",17,170.3),("Van Jefferson",17,168.2),
("Chase Claypool",15,166.6),("Russell Gage Jr.",13,163.0),("Cole Beasley",16,159.3),("K.J. Osborn",17,158.5),
("A.J. Green",16,156.8),("Tim Patrick",16,156.4),("Marquez Callaway",17,151.8),("Courtland Sutton",17,150.2),
("Cedrick Wilson Jr.",14,147.8),("DeAndre Hopkins",10,147.2),("Allen Lazard",14,142.5),("Mecole Hardman Jr.",17,140.9),
("Robbie Chosen",17,138.5),("Elijah Moore",11,138.2),("Robert Woods",9,137.2),("Jarvis Landry",12,133.0),
("Kalif Raymond",16,132.4),("Emmanuel Sanders",14,131.7),("Odell Beckham Jr.",14,129.1),("Laviska Shenault Jr.",16,127.0),
("Byron Pringle",16,126.8),("Gabe Davis",15,125.9),("Antonio Brown",7,121.1),("Braxton Berrios",16,121.1),
("Quez Watkins",17,116.0),("Deonte Harty",13,113.1),("Jamison Crowder",12,109.7),("Donovan Peoples-Jones",14,109.7),
("Bryan Edwards",16,109.1),("Nick Westbrook-Ikhine",15,107.6),("Zay Jones",15,105.9),("Corey Davis",9,105.2),
("DeVante Parker",10,103.5),("Rashod Bateman",12,103.5),("Nelson Agholor",15,103.4),("Jalen Guyton",16,97.2),
("Zach Pascal",16,94.5),("Randall Cobb",11,93.6),("Joshua Palmer",15,92.9),("Michael Gallup",9,91.5),
("Olamide Zaccheaus",15,89.8),("Kenny Golladay",14,89.1),("Tre'Quan Smith",10,87.7),("Allen Robinson II",12,87.0),
("Marquez Valdes-Scantling",11,87.0),("DeAndre Carter",17,86.5),("Freddie Swain",17,86.5),("Jerry Jeudy",10,85.0),
("Henry Ruggs III",7,84.5),("Nico Collins",14,83.6),("Devin Duvernay",16,83.2),("Laquon Treadwell",12,82.4),
("Kadarius Toney",9,82.4),("Jauan Jennings",13,82.2),("Josh Reynolds",11,80.6),("Julio Jones",10,80.4),
("Adam Humphries",17,79.3),("Keelan Cole Sr.",14,78.9),("Jalen Reagor",17,78.1),
]
act_te = [
("Mark Andrews",17,301.1),("Travis Kelce",16,262.8),("Dalton Schultz",17,208.8),("George Kittle",14,198.0),
("Zach Ertz",17,180.7),("Kyle Pitts Sr.",17,176.6),("Rob Gronkowski",12,171.2),("Dallas Goedert",15,165.0),
("Mike Gesicki",17,165.0),("Hunter Henry",16,164.3),("Dawson Knox",15,164.1),("Noah Fant",16,159.0),
("Pat Freiermuth",16,151.7),("Tyler Higbee",15,147.0),("T.J. Hockenson",12,145.3),("Tyler Conklin",17,138.3),
("Darren Waller",11,133.5),("Jared Cook",16,132.4),("C.J. Uzomah",16,128.3),("Taysom Hill",12,126.8),
("Cole Kmet",17,121.2),("Gerald Everett",15,117.8),("David Njoku",15,107.6),("Evan Engram",15,102.5),
("Austin Hooper",15,92.5),("Foster Moreau",15,85.3),("Mo Alie-Cox",17,79.6),("Jack Doyle",15,79.2),
("Anthony Firkser",15,79.1),("Cameron Brate",16,78.5),("Albert Okwuegbunam Jr.",14,76.0),("Dan Arnold",11,75.8),
("Geoff Swaim",16,70.0),("Durham Smythe",16,70.0),("Ricky Seals-Jones",11,69.1),("Jonnu Smith",16,67.4),
("Ryan Griffin",14,65.1),("Hayden Hurst",12,64.1),("Adam Trautman",11,63.3),("Harrison Bryant",15,62.3),
("Josiah Deguara",14,61.5),("Kyle Rudolph",15,59.7),
]

# ---------------- Games played (FantasyPros season stat pages, G column) ----------------
g19_qb = [("Lamar Jackson",15),("Dak Prescott",16),("Jameis Winston",16),("Russell Wilson",16),("Deshaun Watson",15),
("Josh Allen",16),("Kyler Murray",16),("Patrick Mahomes II",14),("Carson Wentz",16),("Aaron Rodgers",16),
("Matt Ryan",15),("Tom Brady",16),("Jared Goff",16),("Jimmy Garoppolo",16),("Philip Rivers",16),
("Ryan Fitzpatrick",15),("Derek Carr",16),("Kirk Cousins",15),("Baker Mayfield",16),("Gardner Minshew II",14),
("Ryan Tannehill",12),("Drew Brees",11),("Daniel Jones",13),("Jacoby Brissett",15),("Andy Dalton",13),
("Mitchell Trubisky",15),("Sam Darnold",13),("Kyle Allen",14),("Matthew Stafford",8),("Mason Rudolph",10),
("Case Keenum",10),("Teddy Bridgewater",10),("Joe Flacco",8),("Marcus Mariota",7),("Drew Lock",5),
("Jeff Driskel",4),("David Blough",5),("Devlin Hodges",8),("Eli Manning",4),("Matt Moore",6),
("Nick Foles",4),("Brandon Allen",3),("Matt Schaub",7),("Chase Daniel",5),("Ryan Finley",3),
("Brian Hoyer",5),("Josh Rosen",6),("Robert Griffin III",7),("AJ McCarron",3),("Cam Newton",2),
("Ben Roethlisberger",2),("Luke Falk",3),("Matt Barkley",3),("Brett Hundley",3),("Tyrod Taylor",8)]
g19_rb = [("Christian McCaffrey",16),("Aaron Jones Sr.",16),("Ezekiel Elliott",16),("Austin Ekeler",16),("Derrick Henry",15),
("Dalvin Cook",14),("Leonard Fournette",15),("Nick Chubb",16),("Alvin Kamara",14),("Saquon Barkley",13),
("Mark Ingram II",15),("Chris Carson",15),("Joe Mixon",16),("Todd Gurley II",15),("Miles Sanders",16),
("Le'Veon Bell",15),("Kenyan Drake",14),("James White",15),("Phillip Lindsay",16),("Devonta Freeman",14),
("Josh Jacobs",13),("Marlon Mack",14),("Melvin Gordon III",12),("David Montgomery",16),("Ronald Jones II",16),
("Raheem Mostert",16),("Tarik Cohen",16),("Latavius Murray",16),("Duke Johnson Jr.",16),("Carlos Hyde",16),
("Sony Michel",16),("Devin Singletary",12),("Adrian Peterson",16),("Jamaal Williams",14),("James Conner",10),
("Royce Freeman",16),("David Johnson",13),("Damien Williams",11),("Tevin Coleman",14),("DeAndre Washington",16),
("LeSean McCoy",13),("Nyheim Miller-Hines",16),("Peyton Barber",16),("Jordan Howard",10),("Jaylen Samuels",14),
("Matt Breida",13),("Kareem Hunt",9),("Rex Burkhead",13),("Boston Scott",11),("Frank Gore",16),
("Chris Thompson",11),("Gus Edwards",16),("Tony Pollard",15),("Kerryon Johnson",8),("J.D. McKissic",16),
("Jalen Richard",16),("Chase Edmonds",13),("Dare Ogunbowale",16),("Rashaad Penny",10),("Alexander Mattison",13),
("Giovani Bernard",16),("Patrick Laird",15),("Darrel Williams",12),("Brian Hill",12),("Dion Lewis",16),
("Ty Johnson",16),("Malcolm Brown",14),("Benny Snell Jr.",13),("Derrius Guice",5),("Jordan Wilkins",14),
("Kalen Ballage",12),("Ryquell Armstead",16),("Brandon Bolden",15),("Kyle Juszczyk",12),("Mike Boone",16),
("Justice Hill",16),("Wayne Gallman Jr.",10),("Jeff Wilson Jr.",11),("Bo Scarbrough",6),("Mark Walton",7),
("Jonathan Williams",9),("Ameer Abdullah",16),("Dontrell Hilliard",14),("C.J. Ham",16),("Ito Smith",7),
("Bilal Powell",14),("Ty Montgomery II",16),("Darwin Thompson",12),("Myles Gaskin",7),("Justin Jackson",7),
("Qadree Ollison",8),("T.J. Yeldon",6),("Reggie Bonnafon",16),("C.J. Prosise",9),("Travis Homer",16)]
g19_wr = [("Michael Thomas",16),("Chris Godwin Jr.",14),("Julio Jones",15),("Cooper Kupp",16),("DeAndre Hopkins",15),
("Keenan Allen",16),("Julian Edelman",16),("Allen Robinson II",16),("Kenny Golladay",16),("Amari Cooper",16),
("DeVante Parker",16),("Jarvis Landry",16),("Tyler Lockett",16),("Robert Woods",15),("Mike Evans",13),
("DJ Moore",15),("DJ Chark Jr.",15),("Tyler Boyd",16),("Courtland Sutton",16),("John Brown",15),
("A.J. Brown",16),("Davante Adams",12),("Michael Gallup",14),("Stefon Diggs",15),("Odell Beckham Jr.",16),
("Jamison Crowder",16),("Calvin Ridley",13),("Marvin Jones Jr.",13),("Terry McLaurin",14),("Emmanuel Sanders",17),
("Deebo Samuel Sr.",15),("Tyreek Hill",12),("DK Metcalf",16),("Cole Beasley",15),("Larry Fitzgerald",16),
("Curtis Samuel",16),("Darius Slayton",14),("Christian Kirk",13),("Diontae Johnson",16),("Robbie Chosen",16),
("Mike Williams",15),("Dede Westbrook",15),("Chris Conley",16),("Randall Cobb",15),("Golden Tate",11),
("Hollywood Brown",14),("Tyrell Williams",14),("Sterling Shepard",10),("Danny Amendola",15),("Sammy Watkins",14),
("Breshad Perriman",14),("Zach Pascal",16),("William Fuller V",11),("James Washington",15),("Hunter Renfrow",13),
("Anthony Miller",16),("T.Y. Hilton",10),("Mohamed Sanu Sr.",15),("Alshon Jeffery",10),("Kenny Stills",13),
("Mecole Hardman Jr.",16),("Brandin Cooks",14),("Corey Davis",15),("Adam Thielen",10),("JuJu Smith-Schuster",12),
("Steven Sims Jr.",16),("Allen Lazard",16),("Auden Tate",13),("Demarcus Robinson",16),("Phillip Dorsett II",14),
("Russell Gage Jr.",16),("Kendrick Bourne",16),("Alex Erickson",16),("Willie Snead IV",16),("John Ross",8),
("Nelson Agholor",11),("Preston Williams",8),("Taylor Gabriel",9),("Albert Wilson",13),("Adam Humphries",12),
("Ted Ginn Jr.",16),("Demaryius Thomas",11),("Allen Hurns",14),("Marquez Valdes-Scantling",16),("Tajae Sharpe",15),
("Bisi Johnson",16),("Keelan Cole Sr.",16),("Geronimo Allison",16),("Josh Gordon",11),("Damiere Byrd",11),
("Tre'Quan Smith",11),("Kelvin Harmon",16),("Cody Latimer",15),("Paul Richardson Jr.",10),("DaeSean Hamilton",16)]
g19_te = [("Travis Kelce",16),("George Kittle",14),("Darren Waller",16),("Zach Ertz",15),("Mark Andrews",15),
("Austin Hooper",13),("Jared Cook",14),("Tyler Higbee",15),("Hunter Henry",12),("Dallas Goedert",15),
("Jason Witten",16),("Mike Gesicki",16),("Greg Olsen",14),("Kyle Rudolph",16),("Jack Doyle",16),
("Noah Fant",16),("Darren Fells",16),("Evan Engram",8),("Tyler Eifert",16),("Jonnu Smith",16),
("Jimmy Graham",16),("Ryan Griffin",13),("Jacob Hollister",11),("Cameron Brate",16),("Jordan Akins",16),
("Gerald Everett",13),("Eric Ebron",11),("Blake Jarwin",16),("O.J. Howard",14),("Vance McDonald",14),
("T.J. Hockenson",12),("Dawson Knox",15),("Irv Smith Jr.",16),("Hayden Hurst",16),("Kaden Smith",9),
("Nick Boyle",16),("Will Dissly",6),("Foster Moreau",13),("Josh Hill",16),("C.J. Uzomah",16),
("Ricky Seals-Jones",14),("Jeremy Sprinkle",16),("Delanie Walker",7),("Demetrius Harris",15),("Charles Clay",15),
("James O'Shaughnessy",5),("Maxx Williams",16),("Rhett Ellison",10),("Anthony Firkser",15),("Logan Thomas",16),
("Marcedes Lewis",16),("Ross Dwelley",16),("Ian Thomas",16),("Benjamin Watson",10),("Nick Vannett",16),
("Dan Arnold",6),("Derek Carrier",16),("Matt LaCosse",12),("Jeff Heuerman",14),("Jesse James",16)]

g20_qb = [("Josh Allen",16),("Kyler Murray",16),("Aaron Rodgers",16),("Patrick Mahomes II",15),("Deshaun Watson",16),
("Russell Wilson",16),("Ryan Tannehill",16),("Tom Brady",16),("Justin Herbert",15),("Lamar Jackson",15),
("Kirk Cousins",16),("Matt Ryan",16),("Derek Carr",16),("Ben Roethlisberger",15),("Cam Newton",15),
("Matthew Stafford",16),("Baker Mayfield",16),("Jared Goff",15),("Teddy Bridgewater",15),("Philip Rivers",16),
("Drew Brees",12),("Carson Wentz",12),("Drew Lock",13),("Daniel Jones",14),("Joe Burrow",10),
("Gardner Minshew II",9),("Mitchell Trubisky",10),("Ryan Fitzpatrick",10),("Sam Darnold",12),("Andy Dalton",11),
("Tua Tagovailoa",10),("Dak Prescott",5),("Nick Mullens",10),("Jalen Hurts",15),("Nick Foles",9),
("Alex Smith",8),("Jimmy Garoppolo",6),("Mike Glennon",5),("Joe Flacco",5),("Brandon Allen",5),
("C.J. Beathard",6),("Kyle Allen",4),("Jake Luton",3),("Jeff Driskel",3),("Marcus Mariota",1),
("Chad Henne",3),("Ryan Finley",5),("Jacoby Brissett",11),("Mason Rudolph",5),("Colt McCoy",4),
("Jarrett Stidham",5),("Garrett Gilbert",2),("Brett Rypien",3),("Blaine Gabbert",4),("Chase Daniel",4)]
g20_rb = [("Alvin Kamara",15),("Dalvin Cook",14),("Derrick Henry",16),("David Montgomery",15),("Aaron Jones Sr.",14),
("Jonathan Taylor",15),("James Robinson",14),("Josh Jacobs",15),("Ezekiel Elliott",15),("Kareem Hunt",16),
("Nick Chubb",12),("Mike Davis",15),("Antonio Gibson",14),("Melvin Gordon III",15),("Nyheim Miller-Hines",16),
("Kenyan Drake",15),("J.D. McKissic",16),("D'Andre Swift",13),("Chris Carson",12),("Ronald Jones II",14),
("David Johnson",12),("Clyde Edwards-Helaire",13),("Miles Sanders",12),("J.K. Dobbins",15),("Chase Edmonds",16),
("Austin Ekeler",10),("James Conner",13),("Myles Gaskin",10),("Todd Gurley II",15),("Giovani Bernard",16),
("Devin Singletary",16),("Jeff Wilson Jr.",12),("Wayne Gallman Jr.",15),("Latavius Murray",15),("Leonard Fournette",13),
("Darrell Henderson Jr.",15),("Gus Edwards",16),("Jamaal Williams",14),("Jerick McKinnon",16),("Adrian Peterson",16),
("Tony Pollard",16),("James White",14),("Malcolm Brown",16),("Rex Burkhead",10),("Cam Akers",12),
("Zack Moss",13),("Frank Gore",15),("Raheem Mostert",8),("Joe Mixon",6),("Boston Scott",16),
("Brian Hill",16),("Kalen Ballage",11),("Damien Harris",10),("Christian McCaffrey",3),("Alexander Mattison",13),
("Devontae Booker",16),("Carlos Hyde",10),("Duke Johnson Jr.",11),("Kyle Juszczyk",16),("Joshua Kelley",14),
("Sony Michel",9),("Benny Snell Jr.",16),("Le'Veon Bell",11),("Kerryon Johnson",16),("Salvon Ahmed",6),
("Phillip Lindsay",11),("Samaje Perine",16),("Justin Jackson",9),("Ty Johnson",13),("Jordan Wilkins",15),
("Ito Smith",14),("Dion Lewis",16),("DeeJay Dallas",12),("Cordarrelle Patterson",16),("Peyton Barber",16),
("Darrel Williams",16),("Mark Ingram II",11),("La'Mical Perine",10),("Jalen Richard",13),("Jeremy McNichols",16),
("Chris Thompson",8),("Matt Breida",12),("Alfred Morris",9),("AJ Dillon",11),("Royce Freeman",16),
("Josh Adams",8),("Rodney Smith",7),("Devonta Freeman",5),("Darwin Thompson",13),("Travis Homer",9),
("JaMycal Hasty",8),("Jordan Howard",7),("Ameer Abdullah",16)]
g20_wr = [("Davante Adams",14),("Tyreek Hill",15),("Stefon Diggs",16),("DeAndre Hopkins",16),("Calvin Ridley",15),
("Justin Jefferson",16),("DK Metcalf",16),("Tyler Lockett",16),("Allen Robinson II",16),("Adam Thielen",15),
("Mike Evans",16),("A.J. Brown",14),("Robert Woods",16),("Keenan Allen",14),("Amari Cooper",16),
("JuJu Smith-Schuster",16),("Brandin Cooks",15),("Marvin Jones Jr.",16),("Robbie Chosen",16),("Terry McLaurin",15),
("Diontae Johnson",15),("CeeDee Lamb",16),("Chase Claypool",16),("Curtis Samuel",15),("DJ Moore",15),
("Cooper Kupp",15),("Cole Beasley",15),("Tee Higgins",16),("Tyler Boyd",15),("Corey Davis",14),
("Chris Godwin Jr.",12),("William Fuller V",11),("Jarvis Landry",15),("Nelson Agholor",16),("Brandon Aiyuk",12),
("Hollywood Brown",16),("Russell Gage Jr.",16),("Michael Gallup",16),("Jamison Crowder",12),("DeVante Parker",14),
("Emmanuel Sanders",14),("T.Y. Hilton",15),("Sterling Shepard",12),("Tim Patrick",15),("Jerry Jeudy",16),
("Laviska Shenault Jr.",14),("Keelan Cole Sr.",16),("Mike Williams",15),("DJ Chark Jr.",13),("Darnell Mooney",16),
("Christian Kirk",14),("Julio Jones",9),("Jakobi Meyers",14),("Darius Slayton",16),("Marquez Valdes-Scantling",16),
("Zach Pascal",16),("Gabe Davis",16),("Greg Ward",16),("Hunter Renfrow",16),("Kendrick Bourne",15),
("Mecole Hardman Jr.",16),("Josh Reynolds",16),("Rashard Higgins",13),("David Moore",16),("Antonio Brown",8),
("Travis Fulgham",13),("Damiere Byrd",16),("A.J. Green",16),("Anthony Miller",16),("Demarcus Robinson",15),
("Danny Amendola",14),("Tre'Quan Smith",14),("Scotty Miller",16),("Larry Fitzgerald",13),("Randall Cobb",10),
("Isaiah McKenzie",16),("James Washington",16),("Breshad Perriman",12),("Michael Pittman Jr.",13),("Allen Lazard",10),
("Braxton Berrios",16),("Chris Conley",15),("Jalen Guyton",16),("John Brown",9),("Willie Snead IV",13),
("KJ Hamler",13),("Sammy Watkins",10),("Jakeem Grant Sr.",14),("Jalen Reagor",11),("Keke Coutee",8),
("Odell Beckham Jr.",7),("Golden Tate",12),("Cam Sims",16),("Henry Ruggs III",13),("Michael Thomas",7)]
g20_te = [("Travis Kelce",15),("Darren Waller",16),("Logan Thomas",16),("Robert Tonyan",16),("T.J. Hockenson",16),
("Mark Andrews",14),("Mike Gesicki",15),("Taysom Hill",16),("Rob Gronkowski",16),("Noah Fant",15),
("Hayden Hurst",16),("Dalton Schultz",16),("Hunter Henry",14),("Jimmy Graham",16),("Eric Ebron",15),
("Evan Engram",16),("Jonnu Smith",15),("Tyler Higbee",15),("Jared Cook",15),("George Kittle",8),
("Dallas Goedert",11),("Austin Hooper",13),("Irv Smith Jr.",13),("Dan Arnold",16),("Gerald Everett",16),
("Anthony Firkser",16),("Jordan Akins",13),("Trey Burton",13),("Tyler Eifert",15),("Mo Alie-Cox",15),
("Drew Sample",16),("Zach Ertz",11),("Darren Fells",16),("Chris Herndon IV",16),("Jordan Reed",10),
("Richard Rodgers",14),("Cameron Brate",16),("Dawson Knox",12),("Jacob Hollister",16),("Kyle Rudolph",12),
("Jack Doyle",14),("Cole Kmet",16),("Harrison Bryant",15),("Will Dissly",16),("Durham Smythe",15),
("James O'Shaughnessy",15),("Greg Olsen",11),("David Njoku",13),("Ross Dwelley",16),("Adam Shaheen",16),
("Tyler Conklin",16),("Donald Parham Jr.",13),("Pharaoh Brown",13),("Tyler Kroft",10),("Ian Thomas",16),
("Jesse James",16),("Marcedes Lewis",15),("Adam Trautman",15),("O.J. Howard",4),("Nick Boyle",9)]

out = {}
out["adp2021"] = [{"name": n, "pos": p, "team": t, "adp": a} for n, p, t, a in adp_rows]

proj = []
for n, t, f in proj_qb:
    proj.append({"name": n, "pos": "QB", "proj": round(f, 1)})
for lst, pos in ((proj_rb, "RB"), (proj_wr, "WR"), (proj_te, "TE")):
    for n, t, rec, f in lst:
        proj.append({"name": n, "pos": pos, "proj": round(f + 0.5 * rec, 1)})
out["proj2021"] = proj

act = []
for lst, pos in ((act_qb, "QB"), (act_rb, "RB"), (act_wr, "WR"), (act_te, "TE")):
    for n, g, pts in lst:
        act.append({"name": n, "pos": pos, "pts": pts, "games": g})
out["actual2021"] = act

def gamelist(qb, rb, wr, te):
    rows, seen = [], set()
    for lst, pos in ((qb, "QB"), (rb, "RB"), (wr, "WR"), (te, "TE")):
        for n, g in lst:
            key = (n, pos)
            if key in seen:
                continue
            seen.add(key)
            rows.append([n, pos, g])
    return rows

out["games2019"] = gamelist(g19_qb, g19_rb, g19_wr, g19_te)
out["games2020"] = gamelist(g20_qb, g20_rb, g20_wr, g20_te)

out["notes"] = (
    "Sources: adp2021 = FantasyFootballCalculator PPR 12-team 2021 preseason ADP (177 QB/RB/WR/TE rows, table ranks 1-211 "
    "with K/DST rows dropped; 'adp' is the overall average pick). proj2021 = FFToday 2021 preseason projections "
    "(playerproj.php PosID 10/20/30/40, default scoring). SCORING VERIFIED against raw stat rows: FFToday default FPts for "
    "RB/WR/TE = 0.1/rush-rec yd + 6/TD + 0.5/reception (half-PPR); converted here to full PPR as proj = FPts + 0.5*Rec "
    "(exact match checked for McCaffrey/Cook/Henry/Kamara/Chark/Kelce/Waller/Kittle). QB FPts verified = 0.04/pass yd + "
    "4/pass TD + 0.1/rush yd + 6/rush TD with NO INT penalty (Allen/Mahomes/Wilson exact); used as-is since QBs have no "
    "receptions, but note QB projections run ~7-15 pts hot vs FantasyPros actuals which subtract 1/INT. actual2021 = "
    "FantasyPros season totals PPR (stats/{qb,rb,wr,te}.php?year=2021&scoring=PPR), 17-game season; FantasyPros QB scoring "
    "= 0.04/pass yd, 4/pass TD, -1 INT (verified vs Josh Allen 417.7). games2019/games2020 = G column from same FantasyPros "
    "stat pages for 2019 and 2020 (16-game seasons), top ~55 QB / ~90-95 RB / ~95 WR / ~60 TE per year. CAVEATS: (1) Names "
    "are as currently rendered by each source, which retro-applies later name changes/suffixes - cross-source joins need "
    "normalization, e.g. Robbie Chosen = Robby Anderson, Nyheim Miller-Hines = Nyheim Hines, Hollywood Brown = Marquise "
    "Brown, Patrick Mahomes vs Patrick Mahomes II, Aaron Jones vs Aaron Jones Sr., Kyle Pitts vs Kyle Pitts Sr., D.J./DJ "
    "variants, Kenny/Kenneth Gainwell, Deonte Harty = Deonte Harris, William Fuller V = Will Fuller. (2) FFC ADP team tags "
    "reflect the site's current data (e.g. Phillip Lindsay listed MIA; FFToday had him HOU). (3) FFToday proj teams use JAC, "
    "FFC uses JAX. (4) games2020 RB ranks 94-95 may be missing (source chunk overlapped by two rows; deduped). (5) 2021 "
    "actuals include only top 38 QB / 75 RB / 95 WR / 42 TE - players outside these ranges (e.g. 2021 preseason draftees "
    "who busted completely) are absent and should be treated as ~0 PPR, not missing-at-random. Collected 2026-08-16 via "
    "WebFetch; quoted numbers only, no computed stats beyond the stated PPR conversion."
)

with open("/home/claude/work/data2/oos2021.json", "w") as f:
    json.dump(out, f, indent=1)

# summary
from collections import Counter
def cnt(rows, key="pos"):
    return dict(Counter(r[key] if isinstance(r, dict) else r[1] for r in rows))
print("adp2021:", len(out["adp2021"]), cnt(out["adp2021"]))
print("proj2021:", len(out["proj2021"]), cnt(out["proj2021"]))
print("actual2021:", len(out["actual2021"]), cnt(out["actual2021"]))
print("games2019:", len(out["games2019"]), cnt(out["games2019"]))
print("games2020:", len(out["games2020"]), cnt(out["games2020"]))
# spot checks
pj = {(r["name"], r["pos"]): r["proj"] for r in proj}
assert pj[("Christian McCaffrey", "RB")] == 381.5, pj[("Christian McCaffrey", "RB")]
assert pj[("Davante Adams", "WR")] == 337.9
assert pj[("Travis Kelce", "TE")] == 265.0
assert pj[("Josh Allen", "QB")] == 395.6
print("PPR conversion spot-checks OK")

"""Static health content and emergency data used by CareConnect."""

TIPS = [
    ("💧", "Stay hydrated", "Drink 7 to 8 glasses of water a day; more if it is hot or you exercise."),
    ("😴", "Protect your sleep", "Sleep 7 to 9 hours and keep a fixed bedtime. Avoid screens in bed."),
    ("🚶", "Move every day", "Aim for 30 minutes of brisk walking or activity on most days."),
    ("🥗", "Eat the rainbow", "Fill half your plate with vegetables and fruits. Limit sugary and fried snacks."),
    ("🧘", "Breathe and pause", "Try 5 minutes of slow breathing when stressed. It calms the nervous system."),
    ("🧼", "Wash your hands", "Wash with soap for 20 seconds before meals and after using the toilet."),
    ("🪑", "Fix your posture", "Take a short stretch break every hour of study or screen work."),
    ("👀", "Rest your eyes", "Every 20 minutes look at something 20 feet away for 20 seconds."),
    ("🗣️", "Talk about it", "Sharing worries with a friend, family member or counsellor lightens the load."),
]

CONDITIONS = {
    "🤕 Migraine": ("A recurring headache, often one-sided and throbbing.",
                    "Throbbing pain, nausea, sensitivity to light and sound, sometimes an aura.",
                    "Rest in a dark quiet room, drink water, keep regular meals and sleep, track your triggers.",
                    "Headaches are sudden and severe, follow an injury, or come with weakness, confusion or vision loss."),
    "🍬 Diabetes": ("A condition where blood sugar stays too high.",
                    "Excess thirst, frequent urination, tiredness, blurred vision, slow-healing wounds.",
                    "Balanced meals, regular activity, monitoring sugar and taking medicines as prescribed.",
                    "You have the signs above, or sugar readings are very high or very low."),
    "❤️ Hypertension": ("Blood pressure that stays above the healthy range.",
                        "Often no symptoms. Sometimes headaches or dizziness.",
                        "Reduce salt, stay active, manage stress, avoid tobacco and check BP regularly.",
                        "BP is repeatedly high, or you have chest pain or severe headache."),
    "🌬️ Asthma": ("A condition where the airways swell and narrow.",
                  "Wheezing, cough, chest tightness, shortness of breath.",
                  "Know your triggers, use inhalers correctly and keep an action plan.",
                  "Breathing is hard, your inhaler is not helping, or lips look blue. Seek emergency help."),
    "🧠 Anxiety and stress": ("Persistent worry that affects daily life.",
                              "Racing heart, restlessness, poor sleep, trouble concentrating.",
                              "Slow breathing, exercise, sleep routine, limiting caffeine, talking to someone you trust.",
                              "Worry stops you doing normal activities, or you have panic attacks or thoughts of self-harm."),
    "🤧 Common cold and flu": ("Viral infections of the nose and throat.",
                               "Sneezing, sore throat, cough, fever, body ache.",
                               "Rest, fluids, warm soups, covering coughs and washing hands.",
                               "Fever lasts over 3 days, breathing is difficult or symptoms get worse."),
}

PREVENT = [
    ("🩺 Yearly health check-up", "Check blood pressure, sugar, cholesterol, weight and eyesight once a year."),
    ("💉 Stay vaccinated", "Keep routine vaccines up to date, including tetanus, hepatitis B and the yearly flu shot."),
    ("🦷 Dental care", "Brush twice a day and visit a dentist every 6 months."),
    ("☀️ Sun and skin", "Use sunscreen, cover up in strong sun and check unusual moles."),
    ("🚭 Avoid tobacco and limit alcohol", "These raise the risk of heart disease, cancer and many other illnesses."),
    ("🧠 Look after mental health", "Take breaks, stay connected with people and ask for help early."),
]

AWARE = [
    ("7 April", "World Health Day", "Health for all"),
    ("31 May", "World No Tobacco Day", "Say no to tobacco"),
    ("29 September", "World Heart Day", "Know your blood pressure and cholesterol"),
    ("10 October", "World Mental Health Day", "Talking helps, so reach out"),
    ("October", "Breast Cancer Awareness Month", "Early screening saves lives"),
    ("14 November", "World Diabetes Day", "Know your risk, check your sugar"),
]

NUMBERS = [
    ("National Emergency Number", "112", "Police, fire and medical help, anywhere in India"),
    ("Ambulance", "108", "Free emergency ambulance in most states"),
    ("Medical advisory", "102", "Ambulance for pregnant women and infants"),
    ("Police", "100", "Report crime or immediate danger"),
    ("Fire", "101", "Fire and rescue services"),
    ("Women helpline", "1091", "Support for women in distress"),
    ("Tele-MANAS mental health", "14416", "Free, 24x7 mental health support"),
]

HOSPITALS = [
    ("City Care Hospital", "Hospital", "1.2 km", "011-4000-1111", "24x7 emergency, ICU"),
    ("Sunrise Multispeciality", "Hospital", "2.8 km", "011-4000-2222", "Trauma and cardiac care"),
    ("Metro Ambulance Service", "Ambulance", "0.9 km", "011-4000-3333", "Advanced life support"),
    ("LifeLine Blood Bank", "Blood bank", "3.4 km", "011-4000-4444", "Open 24 hours"),
    ("MedPlus 24x7 Pharmacy", "Pharmacy", "0.6 km", "011-4000-5555", "Open all night"),
    ("Community Health Centre", "Hospital", "4.1 km", "011-4000-6666", "General emergency"),
]

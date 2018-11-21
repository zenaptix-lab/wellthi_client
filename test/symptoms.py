if __name__ == '__main__':
    physical_symptoms = [
        "NONE_OF_THE_ABOVE", "ACNE", "CONGESTION", "BURNING", "COLD", "DIZZY", "FATIGUE", "FEVER",
        "BOWEL", "NAUSEA", "PAIN", "PALPITATIONS", "RASH", "SWEATING", "SWELLING"]
    negative_emotions = [
        "NONE_OF_THE_ABOVE", "ANGRY", "ANXIOUS", "ASHAMED", "BORED", "DISGUSTED", "DISTRACTED",
        "FRUSTRATED", "HOSTILE", "HUMILIATED", "INSECURE", "SAD", "THREATENED"]

    # print(list(physical_symptoms))

    user_symptons = ["COLD", "FEVER", "DIZZY"]


    def encode(emotions):
        enum_value = 0
        for emotion in emotions:
            for symp in physical_symptoms:
                if emotion == symp:
                    print physical_symptoms.index(emotion)
            print("###########################################", emotion)


    encode(user_symptons)

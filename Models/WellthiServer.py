__author__ = 'rikus'
import json
from hrv.classical import frequency_domain, time_domain
from hrv.filters import moving_average
import pandas as pd
import numpy as np
import os
import config
import requests
from dateutil.parser import parse
import calendar


class Biometric(object):
    def __init__(self, user_id, from_id, to, status, val1, val2, val3, val4, val5, val6):
        self.id = user_id
        self.from_id = from_id
        self.to = to
        self.status = status
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3
        self.val4 = val4
        self.val5 = val5
        self.val6 = val6

    @classmethod
    def encode(cls, jsonString):
        try:
            parsed_json = json.loads(jsonString)
            # print(parsed_json['id'])
            if 'id' and 'from' and 'to' and 'status' and 'val1' and 'val2' and 'val3' and 'val4' and 'val5' and 'val6' in parsed_json:
                obj = Biometric(str(parsed_json['id']), parsed_json['from'], parsed_json['to'], parsed_json['status'],
                                parsed_json['val1'],
                                parsed_json['val2'],
                                parsed_json['val3'], parsed_json['val4'], parsed_json['val5'], parsed_json['val6'])
                return obj
        except:
            raise Exception('does not contain all variables needed')

    def decode(self):
        data_dic = self.__dict__
        data_dic['from'] = data_dic[
            'from_id']  # from is a reserved keyword, hence using from_id but server expects from
        del data_dic['from_id']
        data = json.dumps(data_dic)
        return data

    @classmethod
    def getRRIntervals(cls, data):
        # data is read from the csv, and the 2nd column indicates when heart beats occurred with a 'B'

        # Select heartbeats column
        beats = data.loc[:, 1] == 'B'

        # get the index numbers of when "beats" column is    True
        beat_indices_orig = list(beats[beats].index)

        # shift index numbers by 1
        beat_indices_shifted = [x + 1 for x in beat_indices_orig]

        # take the difference between original and shifted beats. This removes consecutive beats in original data
        beat_indices = list(set(beat_indices_orig) - set(beat_indices_shifted))
        beat_indices.sort()

        # Now process RR-intervals (difference in time between beats):
        rr_indices = [t - s for s, t in zip(beat_indices, beat_indices[1:])]
        # This takes the difference between consecutive elements in a list (gets number of samples between beats)

        # There are 60 samples per second, so translate above into milliseconds between beats (RR intervals):
        rr = [i * 1000 / 60.0 for i in rr_indices]
        return rr

    # Process the time domain parameters of HRV from the RR-intervals
    @classmethod
    def getHRV_TimeDomain(cls, rr_intervals):
        return time_domain(rr_intervals)

    # Process the frequency domain parameters of HRV from the RR-intervals
    @classmethod
    def getHRV_FreqDomain(cls, rr_intervals):
        return frequency_domain(rri=rr_intervals, fs=4.0, method='welch', interp_method='cubic', detrend='linear')

    @classmethod
    def evaluateStress(cls, rr_sample):
        s1 = 0  # light indicator of stress
        s2 = 0  # hard indicator of stress

        # Time domain indicators:
        timeDomain = Biometric.getHRV_TimeDomain(rr_sample)

        rr_mean = np.mean(rr_sample)
        if rr_mean < 640:
            s2 = s2 + 1
        else:
            if rr_mean < 780: s1 = s1 + 1

        sdnn = timeDomain["sdnn"]
        if sdnn < 20:
            s2 = s2 + 1
        else:
            if sdnn < 40: s1 = s1 + 1

        rmssd = timeDomain["rmssd"]
        if rmssd < 16: s2 = s2 + 1

        # Time domain indicators:
        freqDomain = Biometric.getHRV_FreqDomain(rr_sample)

        hf = freqDomain["hf"]
        if hf < 465:
            s2 = s2 + 1
        else:
            if hf < 700: s1 = s1 + 1

        vlf = freqDomain["vlf"]
        if vlf < 200:
            s2 = s2 + 1
        else:
            if vlf < 300: s1 = s1 + 1

        lf_hf = freqDomain["lf_hf"]
        if lf_hf > 4:
            s2 = s2 + 1
        else:
            if lf_hf > 2.5: s1 = s1 + 1

        #  Summarise result into a binary indicator. If s2 >= 1, or if s1 >= 2, then stressed:
        stressed = 1 if (s2 >= 1) or (s1 >= 2) else 0

        result = {'status': stressed, 'val1': rr_mean, 'val2': sdnn, 'val3': rmssd, 'val4': hf, 'val5': vlf,
                  'val6': lf_hf}

        return result

    @classmethod
    def ingest_biometric_files(cls, user_id):
        known_files = config.FILE_DROP_CONFIG['known_files']
        path_load = config.FILE_DROP_CONFIG['path_load']
        files = os.listdir(path_load)
        for f in files:
            if f not in known_files:
                print("let's go! Read file: " + f)
                data = pd.read_csv(path_load + f, header=None)
                known_files.append(f)

                # user_id = config.FILE_DROP_CONFIG['user_id']
                file_timestamp = config.FILE_DROP_CONFIG['file_timestamp']

                rr = Biometric.getRRIntervals(data)
                # toPrint = np.array2string(np.array(rr))

                # Group rr into 2 minute intervals
                rr_sum = np.cumsum(rr)
                print(rr_sum)

                sample_size = 150000  # milliseconds

                # the last element of the cumulative sum of rr is equal to the total duration of the recording.
                # We want to group the rr values by 2.5 minutes, so that the parameters can be generated for each group
                print(range(0, int(rr_sum[len(rr_sum) - 1].item()), sample_size))

                for i in range(0, int(rr_sum[len(rr_sum) - 1].item()), sample_size):
                    rr_sum_subset = [(i <= s) and (s < (i + 1) * sample_size) for s in rr_sum]
                    rr_temp = np.array(rr)
                    rr_sample = list(rr_temp[rr_sum_subset])
                    if len(
                            rr_sample) > 80:  # Let's require at least 80 rr's to process, in case last group only has a few
                        result = Biometric.evaluateStress(rr_sample)

                        result['id'] = user_id
                        result['from'] = file_timestamp + i / 1000
                        result['to'] = file_timestamp + (i + sample_size) / 1000

                        bio_obj = Biometric(result['id'], result['from'], result['to'], result['status'],
                                            result['val1'],
                                            result['val2'], result['val3'], result['val4'], result['val5'],
                                            result['val6'])

                        formatted_bio = bio_obj.decode()
                        r = requests.post(config.WELLTHI_SERVER_CONFIG['biometric_data_endpoint'] + user_id,
                                          headers={'content-type': 'application/json'},
                                          data=formatted_bio)
                        print "responce to request: ", r

                return "finished processing files"

        return "Okay, no new files"


class Symptoms(object):
    def __init__(self):
        self.physical_symptoms = [
            "NONE_OF_THE_ABOVE", "ACNE", "CONGESTION", "BURNING", "COLD", "DIZZY", "FATIGUE", "FEVER",
            "BOWEL", "NAUSEA", "PAIN", "PALPITATIONS", "RASH", "SWEATING", "SWELLING"]
        self.negative_emotions = [
            "NONE_OF_THE_ABOVE", "ANGRY", "ANXIOUS", "ASHAMED", "BORED", "DISGUSTED", "DISTRACTED",
            "FRUSTRATED", "HOSTILE", "HUMILIATED", "INSECURE", "SAD", "THREATENED"]

    def encode(self, emotions):
        enum_value = 0
        for emotion in emotions:
            if emotion in self.physical_symptoms:
                for symp in self.physical_symptoms:
                    if emotion == symp:
                        index = self.physical_symptoms.index(emotion)
                        enum_value = enum_value + pow(2, index)
            else:
                for emot in self.negative_emotions:
                    if emotion == emot:
                        index = self.negative_emotions.index(emotion)
                        enum_value = enum_value + pow(2, index)
            print("###########################################", emotion)
        return enum_value


class Assessment(object):
    def __init__(self, user_id, at, mental, physical, negative_emotions, physical_symptoms):
        self.id = user_id
        self.at = at
        self.mental = mental
        self.physical = physical
        self.negativeEmotions = negative_emotions
        self.physicalSymptoms = physical_symptoms

    @classmethod
    def encode(self, jsonString):
        try:
            parsed_json = json.loads(jsonString)
            # print(parsed_json['id'])
            if 'id' and 'at' and 'mental' and 'physical' and 'negativeEmotions' and 'physicalSymptoms':
                obj = Assessment(str(parsed_json['id']), parsed_json['at'], parsed_json['mental'],
                                 parsed_json['physical'], parsed_json['negativeEmotions'],
                                 parsed_json['physicalSymptoms'])

                return obj
        except:
            raise Exception('does not contain all variables needed')

    def decode(self):
        data_dic = self.__dict__
        data = json.dumps(data_dic)
        return data

    @classmethod
    def get_assessment(cls, cred, symptoms, todays_current_chat):
        mental = 0
        physical = 0
        neg_emotions = 0
        physical_symptoms = 0

        dt = parse(todays_current_chat[0][0])
        epoch = calendar.timegm(dt.timetuple())
        print("epoch :", epoch)

        for chat in todays_current_chat:
            if len(chat) > 0:
                try:
                    intent = str(chat[2][0]['intent']).lower()
                    chat_text = str(chat[1]['text']).upper()
                    print ("Intent : ", intent)
                    print ("chat text : " + chat_text)

                    if chat_text in symptoms.negative_emotions:
                        print "NEGATIVE_EMOTIONS"
                        neg_emotions = symptoms.encode([chat_text])
                    else:
                        neg_emotions = 0

                    if chat_text in symptoms.physical_symptoms:
                        print "NEGATIVE_PHYSICAL"
                        physical_symptoms = symptoms.encode([chat_text])
                    else:
                        physical_symptoms = 0

                    if "mental_rating" in intent:
                        try:
                            mental = int(str(chat[1]['text'])[1:])
                        except:
                            print "mental not an int"
                    else:
                        mental = 0

                    if "physical_rating" in intent:
                        try:
                            physical = int(str(chat[1]['text'])[1:])
                        except:
                            print "physical not an int"
                    else:
                        physical = 0
                except:
                    print ("Could not post summary of chat ", chat)

        return Assessment(cred.username, epoch, mental, physical, neg_emotions, physical_symptoms)

    def post_assessment(self):
        formatted_asses = self.decode()
        r = requests.post(config.WELLTHI_SERVER_CONFIG['assessment_data_endpoint'] + self.id,
                          headers={'content-type': 'application/json'},
                          data=formatted_asses)

        print "responce to request: ", r

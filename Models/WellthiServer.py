__author__ = 'rikus'
import json


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
    def encode(self, jsonString):
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

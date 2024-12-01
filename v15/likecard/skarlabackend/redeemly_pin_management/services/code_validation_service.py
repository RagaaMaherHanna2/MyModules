import re


class RedeemlyCodeValidationService:
    PARTS_COUNT = 4
    ALPHANUMERIC_SYMBOLS = '0123456789ABCDEFGHJKLMNPQRTUVWXY'
    ALPHA_SYMBOLS = 'ABCDEFGHJKLMNPQRTUVWXY'
    NUMERIC_SYMBOLS = '0987654321'
    PARTS_LENS = [4, 3, 3, 4]

    def __init__(self, code, code_type="alphanumeric"):
        self.code = code
        self.code_type = code_type

    def validate(self, code_type):
        self.code_type = code_type
        input_code = re.sub(r'[^0-9A-Z]+', '', self.code.upper())
        formatted_code = input_code
        if self.code_type == 'alphanumeric':
            formatted_code = input_code.replace('O', '0').replace('I', '1').replace('Z', '2').replace('S', '5')
        elif self.code_type == 'alpha':
            formatted_code = input_code.replace('O', '').replace('I', '').replace('Z', '').replace('S', '')
        validated_code = self._validate_code(formatted_code)
        if validated_code:
            if '-' not in self.code:
                validated_code = validated_code.replace("-", "")
            return validated_code
        return False

    def _validate_code(self, code):
        code_len = sum(self.PARTS_LENS)
        if len(code) != code_len:
            return ''
        temp = code
        parts = []
        for elem in self.PARTS_LENS:
            parts.append(temp[:elem])
            temp = temp[elem:]
        if len(parts) != self.PARTS_COUNT:
            return ''
        part = ''
        for i in range(len(parts)):
            part = parts[i]
            if len(part) != self.PARTS_LENS[i]:
                return ''
            data = part[0: self.PARTS_LENS[i] - 1]
            check = part[-1]
            if check != self._validate_digit_alg(data, i + 1, code_len):
                return ''
        return '-'.join(parts)

    def _validate_digit_alg(self, data, check, code_len):
        symbols_arr = self._get_type_symbols()
        symbols_obj = {}
        for i, symbol in enumerate(symbols_arr):
            symbols_obj[symbol] = i
        for char in data:
            k = symbols_obj[char]
            check = check * (len(symbols_arr) - code_len - 1) + k
        return symbols_arr[check % (len(symbols_arr) - 1)]

    def _get_type_symbols(self):
        if self.code_type == 'alphanumeric':
            symbols_arr = list(self.ALPHANUMERIC_SYMBOLS)
        elif self.code_type == "alpha":
            symbols_arr = list(self.ALPHA_SYMBOLS)
        else:  # numeric  type
            symbols_arr = list(self.NUMERIC_SYMBOLS)
        return symbols_arr

    def validate_code_4_digits(self):
        if self.code.isdigit() and len(self.code) == 4 :
            return True
        else:
            return False
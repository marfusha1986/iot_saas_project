import numpy as np

class KeystrokeAuthEngine:
    @staticmethod
    def calculate_deviation(baseline_vector: list[float],current_vector:list[float],threshold:float=0.2) -> bool:
        """
        Kullanıcının referans tuş vuruş süreleri (baseline) ile
        anlık gelen süreler arasındakı sapmayı hesaplar.
        """

        if not baseline_vector or not current_vector:
            return False

        base = np.array(baseline_vector)
        curr = np.array(current_vector)

        #Ortalama farkın mutlak yüzdesel sapması
        mean_base = np.mean(base)
        mean_curr = np.mean(curr)

        deviation = abs(mean_base - mean_curr) / mean_base

        #Eğer sapma belirlenen eşik değerinin altındaysa kullanıcı doğrulandı sayılır
        return deviation <= threshold
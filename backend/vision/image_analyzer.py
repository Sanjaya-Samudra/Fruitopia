"""Enhanced image analysis beyond classification: ripeness, quality, defect detection."""

import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image, ImageStat


class FruitImageAnalyzer:
    """Analyzes fruit images for ripeness, quality, and defect indicators."""

    RIPENESS_THRESHOLDS = {
        "bananas": {"hue_ripe": (30, 60), "brightness_unripe": 80, "defect_mottled": 0.15},
        "apples": {"hue_ripe": (0, 30), "saturation_ripe": 60, "defect_ratio": 0.1},
        "tomatoes": {"hue_ripe": (0, 20), "saturation_ripe": 70, "defect_ratio": 0.12},
        "strawberries": {"hue_ripe": (0, 15), "saturation_ripe": 80, "defect_ratio": 0.08},
        "oranges": {"hue_ripe": (15, 40), "saturation_ripe": 65, "defect_ratio": 0.1},
        "lemons": {"hue_ripe": (40, 70), "saturation_ripe": 60, "defect_ratio": 0.1},
        "avocados": {"hue_ripe": (90, 140), "darkness_ripe": 100, "defect_ratio": 0.1},
        "mangos": {"hue_ripe": (20, 50), "saturation_ripe": 70, "defect_ratio": 0.1},
        "pineapples": {"hue_ripe": (25, 55), "saturation_ripe": 60, "defect_ratio": 0.1},
        "grapes": {"hue_ripe": (270, 330), "saturation_ripe": 50, "defect_ratio": 0.1},
    }

    def __init__(self):
        pass

    def analyze(self, image_path: str, fruit_class: str = None) -> Dict:
        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)
            hsv = self._rgb_to_hsv(img_array)

            size_analysis = self._analyze_size(img)
            color_analysis = self._analyze_color(hsv, fruit_class)
            texture_analysis = self._analyze_texture(img_array)
            defect_analysis = self._analyze_defects(img_array, hsv)

            ripeness = self._estimate_ripeness(color_analysis, fruit_class)
            quality = self._estimate_quality(defect_analysis, texture_analysis, ripeness)

            return {
                "ripeness": ripeness,
                "quality_score": quality,
                "size": size_analysis,
                "colors": color_analysis,
                "texture": texture_analysis,
                "defects": defect_analysis,
                "confidence": self._calculate_confidence(quality, ripeness),
            }
        except Exception as e:
            return {"error": str(e)}

    def _rgb_to_hsv(self, img_array: np.ndarray) -> np.ndarray:
        from matplotlib.colors import rgb_to_hsv
        return rgb_to_hsv(img_array / 255.0)

    def _analyze_size(self, img: Image.Image) -> Dict:
        w, h = img.size
        total_pixels = int(w * h)
        return {
            "width_px": int(w),
            "height_px": int(h),
            "total_pixels": total_pixels,
            "relative_size": "large" if total_pixels > 500000 else "medium" if total_pixels > 100000 else "small",
        }

    def _analyze_color(self, hsv: np.ndarray, fruit_class: str = None) -> Dict:
        hue = hsv[:, :, 0] * 360
        sat = hsv[:, :, 1] * 100
        val = hsv[:, :, 2] * 100

        hue_mean = float(np.mean(hue))
        sat_mean = float(np.mean(sat))
        val_mean = float(np.mean(val))
        hue_std = float(np.std(hue))

        dominant_hues = self._get_dominant_hues(hue, sat)
        dominant_colors = self._hue_to_name(dominant_hues)

        return {
            "dominant_hues": dominant_hues[:3],
            "dominant_colors": dominant_colors[:3],
            "hue_mean": round(hue_mean, 1),
            "saturation_mean": round(sat_mean, 1),
            "brightness_mean": round(val_mean, 1),
            "color_variance": round(hue_std, 1),
            "is_colorful": bool(sat_mean > 30),
        }

    def _get_dominant_hues(self, hue: np.ndarray, sat: np.ndarray, k: int = 3) -> list:
        mask = sat > 0.3
        hues = hue[mask]
        if len(hues) == 0:
            return [0.0]
        hist, edges = np.histogram(hues, bins=36, range=(0, 360))
        dominant_bins = np.argsort(hist)[-k:][::-1]
        return [float((edges[i] + edges[i + 1]) / 2) for i in dominant_bins if int(hist[i]) > 0]

    def _hue_to_name(self, hues: list) -> list:
        names = []
        for h in hues:
            if h < 15 or h >= 345:
                names.append("red")
            elif h < 45:
                names.append("orange")
            elif h < 75:
                names.append("yellow")
            elif h < 165:
                names.append("green")
            elif h < 195:
                names.append("cyan")
            elif h < 285:
                names.append("blue/purple")
            else:
                names.append("pink/magenta")
        return names

    def _analyze_texture(self, img_array: np.ndarray) -> Dict:
        gray = np.mean(img_array, axis=2)
        grad_x = np.abs(np.diff(gray, axis=1))
        grad_y = np.abs(np.diff(gray, axis=0))

        roughness = float(np.mean(grad_x) + np.mean(grad_y))
        smoothness = float(max(0, 100 - roughness))

        return {
            "roughness": round(roughness, 1),
            "smoothness": round(smoothness, 1),
            "surface_type": "smooth" if smoothness > 70 else "moderate" if smoothness > 40 else "rough",
        }

    def _analyze_defects(self, img_array: np.ndarray, hsv: np.ndarray) -> Dict:
        gray = np.mean(img_array, axis=2)
        val = hsv[:, :, 2]

        dark_spots = int(np.sum(val < 0.2))
        bright_spots = int(np.sum(val > 0.95))
        total_pixels = img_array.shape[0] * img_array.shape[1]

        defect_ratio = float((dark_spots + bright_spots) / total_pixels)
        has_defects = bool(defect_ratio > 0.05)

        if has_defects:
            defect_type = "dark_spots" if dark_spots > bright_spots else "bright_spots"
        else:
            defect_type = "none"

        return {
            "defect_ratio": round(defect_ratio, 3),
            "has_defects": has_defects,
            "defect_type": defect_type,
            "dark_spot_pct": round(dark_spots / total_pixels * 100, 1),
            "bright_spot_pct": round(bright_spots / total_pixels * 100, 1),
        }

    def _estimate_ripeness(self, color: Dict, fruit_class: str = None) -> Dict:
        thresholds = self.RIPENESS_THRESHOLDS.get(fruit_class, {})
        sat = float(color.get("saturation_mean", 50))
        brightness = float(color.get("brightness_mean", 50))

        ripeness_score = 0.5
        ripeness_stage = "unknown"

        if thresholds:
            sat_min = float(thresholds.get("saturation_ripe", 50))
            hue_min, hue_max = thresholds.get("hue_ripe", (0, 360))
            hue = float(color.get("hue_mean", 0))

            sat_factor = min(sat / sat_min, 1.5) if sat_min > 0 else 1.0
            hue_in_range = hue_min <= hue <= hue_max or (hue_max < hue_min and (hue >= hue_min or hue <= hue_max))
            hue_factor = 1.5 if hue_in_range else 0.5

            ripeness_score = float(min((sat_factor * hue_factor) / 2, 1.0))

        if ripeness_score < 0.3:
            ripeness_stage = "unripe"
        elif ripeness_score < 0.6:
            ripeness_stage = "underripe"
        elif ripeness_score < 0.85:
            ripeness_stage = "ripe"
        else:
            ripeness_stage = "overripe"

        return {
            "score": round(ripeness_score, 2),
            "stage": ripeness_stage,
            "label": f"{ripeness_stage} ({int(ripeness_score * 100)}%)",
        }

    def _estimate_quality(self, defects: Dict, texture: Dict, ripeness: Dict) -> float:
        defect_penalty = float(defects.get("defect_ratio", 0)) * 2.0
        ripeness_bonus = 1.0 - abs(float(ripeness.get("score", 0.5)) - 0.7)
        texture_bonus = float(texture.get("smoothness", 50)) / 200.0

        quality = 0.8 - defect_penalty + ripeness_bonus * 0.3 + texture_bonus * 0.2
        return round(float(max(0, min(1, quality))), 2)

    def _calculate_confidence(self, quality: float, ripeness: Dict) -> float:
        base = (float(quality) + float(ripeness.get("score", 0.5))) / 2.0
        return round(float(min(1, base * 1.2)), 2)


class VisionPipeline:
    """Complete vision pipeline combining classification + analysis."""

    def __init__(self):
        self.analyzer = FruitImageAnalyzer()

    def analyze_fruit_image(self, image_path: str, predicted_class: str = None) -> Dict:
        result = {"fruit_class": predicted_class or "unknown"}
        analysis = self.analyzer.analyze(image_path, predicted_class)
        result["analysis"] = analysis
        result["summary"] = self._generate_summary(predicted_class, analysis)
        return result

    def _generate_summary(self, fruit_class: str, analysis: Dict) -> str:
        ripeness = analysis.get("ripeness", {})
        quality = analysis.get("quality_score", 0)
        defects = analysis.get("defects", {})
        colors = analysis.get("colors", {})

        parts = []
        if fruit_class:
            parts.append(f"This appears to be a {fruit_class}")

        stage = ripeness.get("stage", "unknown")
        parts.append(f"that is {stage}")
        if quality > 0.7:
            parts.append("and in excellent condition")
        elif quality > 0.4:
            parts.append("in fair condition")
        else:
            parts.append("showing signs of age or damage")

        if defects.get("has_defects"):
            parts.append(f"with some {defects.get('defect_type', 'imperfections')}")

        if colors.get("dominant_colors"):
            main_color = colors["dominant_colors"][0]
            parts.append(f"({main_color} appearance)")

        rip_score = ripeness.get("score", 0.5)
        if rip_score < 0.3:
            parts.append("- may need more time to ripen")
        elif rip_score > 0.85:
            parts.append("- best consumed soon")

        return ". ".join(parts)


vision_pipeline = VisionPipeline()

import sensor
import image
import time
import ml
import gc
import sys
CONFIDENCE_THRESHOLD = 0.7
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.skip_frames(time=2000)
clock = time.clock()
recommendations = {
    "vegetativ_timpuriu": {
        "healthy":	 "Planta sanatoasa in stadiu timpuriu. Mentineti irigarea si fertilizarea.",
        "brown_rust":  "ATENTIE: Brown Rust detectat! Aplicati fungicid preventiv imediat.",
        "yellow_rust": "ATENTIE: Yellow Rust detectat! Aplicati fungicid sistemic imediat.",
        "leaf_blight": "ATENTIE: Leaf Blight detectat. Reduceti umiditatea si aplicati fungicid.",
        "black_point": "Improbabil in acest stadiu. Verificati pozitionarea camerei.",
        "wheat_blast": "Improbabil in acest stadiu. Verificati pozitionarea camerei."
    },
    "vegetativ_avansat": {
        "healthy":	 "Planta sanatoasa. Pregatiti fertilizarea pentru formarea spicului.",
        "brown_rust":  "ATENTIE: Brown Rust activ! Tratament fungicid urgent necesar.",
        "yellow_rust": "ATENTIE: Yellow Rust avansat! Tratament imediat necesar.",
        "leaf_blight": "ATENTIE: Leaf Blight avansat. Aplicati tratament foliar.",
        "black_point": "Improbabil in acest stadiu. Verificati pozitionarea camerei.",
        "wheat_blast": "Improbabil in acest stadiu. Verificati pozitionarea camerei."
    },
    "maturitate": {
        "healthy":	 "Spic sanatos. Evaluati momentul optim pentru recoltare.",
        "brown_rust":  "Brown Rust la maturitate. Recoltati cat mai curand.",
        "yellow_rust": "Yellow Rust prezent. Recoltati urgent.",
        "leaf_blight": "Leaf Blight la maturitate. Recoltati si evaluati pierderile.",
        "black_point": "ATENTIE: Black Point pe boabe! Verificati calitatea recoltei.",
        "wheat_blast": "PERICOL: Wheat Blast! Consultati specialist inainte de recoltare."
    }
}


def get_recommendation(stage, disease):
    return recommendations.get(stage, {}).get(
        disease, "Stadiu necunoscut. Verificati pozitionarea camerei."
    )


def predict(model_path, labels_path, img):
    net = None
    try:
        gc.collect()
        net = ml.Model(model_path)
        labels = [l.rstrip('\n') for l in open(labels_path)]
        preds = list(zip(labels, net.predict([img])[0].flatten().tolist()))
        preds.sort(key=lambda x: x[1], reverse=True)
        return preds[0]
    except Exception as e:
        print("ERR_MODEL:" + str(e))
        return ("unknown", 0.0)
    finally:
        net = None
        gc.collect()


print("Sistem pornit.")
while True:
    clock.tick()
    gc.collect()
    img = sensor.snapshot()
    img.gaussian(2)
    img.histeq(adaptive=True, clip_limit=3)
    img.laplacian(1, sharpen=True)
    img.median(1, percentile=0.5)
    growth_label, growth_conf = predict(
        "growth_model.tflite",
        "growth_labels.txt",
        img
    )
    disease_label, disease_conf = predict(
        "disease_model.tflite",
        "disease_labels.txt",
        img
    )
    if growth_conf >= CONFIDENCE_THRESHOLD and disease_conf >= CONFIDENCE_THRESHOLD:
        rec = get_recommendation(growth_label, disease_label)
    elif growth_conf < CONFIDENCE_THRESHOLD:
        rec = "Confidenta scazuta pentru stadiu. Repositionati camera."
    else:
        rec = "Confidenta scazuta pentru boala. Apropiati camera."
    fps = clock.fps()
    print("RESULT;STAGE=%s;CONF_STAGE=%.2f;DISEASE=%s;CONF_DISEASE=%.2f;RECOMM=%s;FPS=%.1f" % (
        growth_label, growth_conf,
        disease_label, disease_conf,
        rec, fps
    ))
    time.sleep_ms(3000)

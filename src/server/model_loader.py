import torch
import timm
from PIL import Image
import io
import base64
from transformers import AutoConfig, AutoModelForImageClassification, AutoFeatureExtractor

def load_disease_model(model_dir):
    config = AutoConfig.from_pretrained(model_dir)
    model = AutoModelForImageClassification.from_pretrained(model_dir, config=config)
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_dir)
    model.eval()
    return model, feature_extractor

def preprocess_disease_image(base64_image, feature_extractor):
    from PIL import Image
    import io
    import base64

    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
    return inputs

# Load model
def load_model(model_path):
    model = timm.create_model('vit_base_patch14_reg4_dinov2.lvd142m_in1k', pretrained=False, num_classes=7806)
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['state_dict'], strict=False)
    model.eval()
    return model

# Load class mapping
def load_class_mapping(mapping_path):
    class_map = {}
    with open(mapping_path, 'r') as f:
        for line in f:
            index, species_id = line.strip().split()
            class_map[int(index)] = species_id
    return class_map

# Preprocess image
from torchvision import transforms

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def preprocess_image(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    return preprocess(image).unsqueeze(0)  # Add batch dimension

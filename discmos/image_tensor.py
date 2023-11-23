import torch
import torchvision
import torchvision.transforms.functional
from PIL import Image


def image_to_tensor(image: Image.Image) -> torch.Tensor:
    tensor = torchvision.transforms.PILToTensor()(image)
    return tensor


def tensor_to_image(tensor: torch.tensor) -> Image.Image:
    image = torchvision.transforms.ToPILImage()(tensor)
    return image

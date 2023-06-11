from align_face import *
from model import *
from PIL import Image
from tqdm import tqdm


_TAGS = "5_o_Clock_Shadow Arched_Eyebrows Attractive Bags_Under_Eyes Bald Bangs Big_Lips Big_Nose Black_Hair Blond_Hair Blurry Brown_Hair Bushy_Eyebrows Chubby Double_Chin Eyeglasses Goatee Gray_Hair Heavy_Makeup High_Cheekbones Male Mouth_Slightly_Open Mustache Narrow_Eyes No_Beard Oval_Face Pale_Skin Pointy_Nose Receding_Hairline Rosy_Cheeks Sideburns Smiling Straight_Hair Wavy_Hair Wearing_Earrings Wearing_Hat Wearing_Lipstick Wearing_Necklace Wearing_Necktie Young"
_TAGS = _TAGS.split()


if __name__ == '__main__':

    imgtest = align('test/mypic.jpg')
    imgal, _ = align_face(imgtest)

    # Encoding speed
    eps = encode(imgal)
    t = time.time()
    for _ in tqdm(range(10)):
        eps = encode(imgal)
    print("Encoding latency {} sec/img".format((time.time() - t) / (1 * 10)))

    # # Decoding speed
    # dec = decode(eps)
    # t = time.time()
    # for _ in tqdm(range(10)):
    #     dec = decode(eps)
    # print("Decoding latency {} sec/img".format((time.time() - t) / (1 * 10)))
    # img = Image.fromarray(dec[0])
    # img.save('test/dec2.png')

    # Manipulation
    dec, _ = manipulate(eps, _TAGS.index('Young'), 1.10)
    img = Image.fromarray(dec[0])
    img.save('test/old.png')

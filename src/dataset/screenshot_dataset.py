# from skimage import io
# from torch.utils.data import Dataset

# unused dataset implementation approach
# class ScreenshotDataset(Dataset):
#     def __init__(self, name, screenshot_paths):
#         self.name = name
#         self.screenshot_paths = screenshot_paths

#     def __len__(self):
#         return len(self.screenshot_paths)

#     def __getitem__(self):
#         path = screenshot_paths.pop(0)
#         screenshot = io.imread(path)
#         return screenshot

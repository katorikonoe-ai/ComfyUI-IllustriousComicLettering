# Cập nhật và đăng Illustrious Comic Lettering v1.1.0

## Bản này thay đổi gì?

- Thêm `bubble_width_limit` (mặc định `45`).
- Thêm `tail_length` (mặc định `42`).
- Thêm `tail_width` (mặc định `22`).
- Thêm `bubble_top_offset` (mặc định `26`).
- Đổi font mặc định sang `DejaVuSans.ttf`.
- Giữ nguyên node type `IllustriousComicLettering4Panel`, nên workflow cũ vẫn nhận đúng node.

## 1. Cập nhật GitHub

Cách dễ nhất là giải nén `ComfyUI-IllustriousComicLettering-v1.1.0.zip`, rồi dùng GitHub Desktop hoặc Git để chép đè nội dung repository hiện tại.

PowerShell (mỗi lệnh chạy trên một dòng):

```powershell
cd "D:\New Workflow"

$gitExe = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"

& $gitExe clone "https://github.com/katorikonoe-ai/ComfyUI-IllustriousComicLettering.git" "ComfyUI-IllustriousComicLettering-Publish"

Copy-Item -Path "D:\New Workflow\ComfyUI-IllustriousComicLettering\*" -Destination "D:\New Workflow\ComfyUI-IllustriousComicLettering-Publish" -Recurse -Force

cd "D:\New Workflow\ComfyUI-IllustriousComicLettering-Publish"

& $gitExe add .
& $gitExe commit -m "Release v1.1.0: configurable bubbles and tails"
& $gitExe push origin main
```

Nếu Git hỏi đăng nhập, đăng nhập tài khoản GitHub `katorikonoe-ai`. Không nhập API key Comfy Registry vào GitHub.

## 2. Tạo GitHub Release

1. Mở repository trên GitHub.
2. Chọn **Releases** → **Draft a new release**.
3. Tạo tag `v1.1.0` và title `v1.1.0`.
4. Upload file `ComfyUI-IllustriousComicLettering-v1.1.0.zip`.
5. Chọn **Publish release**.

## 3. Cập nhật Comfy Registry

Không cần tạo API key mới. Key cũ vẫn dùng được nếu chưa bị thu hồi.

Chạy trong bản clone có `.git`:

```powershell
cd "D:\New Workflow\ComfyUI-IllustriousComicLettering-Publish"

$gitExe = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"
$env:GIT_PYTHON_GIT_EXECUTABLE = $gitExe
$gitFolder = Split-Path $gitExe
$env:Path = "$gitFolder;$env:Path"
$env:PYTHONUTF8 = "1"

py -m comfy_cli node publish
```

Khi được hỏi tracking, chọn `N` nếu không muốn gửi thống kê. Nếu CLI yêu cầu API key, dùng lại key cũ của publisher `katorikonoe`.

Registry sẽ cập nhật cùng package hiện tại vì tên package và PublisherId không đổi; chỉ version tăng từ `1.0.0` lên `1.1.0`.

## 4. Kiểm tra trong ComfyUI/Floyo

1. Update hoặc cài lại node.
2. Khởi động lại ComfyUI/Floyo.
3. Xóa node lettering cũ khỏi canvas rồi thêm lại nếu bốn input mới chưa xuất hiện.
4. Dùng preset: `45 / 42 / 22 / 26`.

export async function compressCommentImage(file: File): Promise<File> {
  const bitmap = await loadImage(file);
  const maxSide = 1280;
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
  const width = Math.max(1, Math.round(bitmap.width * scale));
  const height = Math.max(1, Math.round(bitmap.height * scale));

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("图片压缩失败");
  context.drawImage(bitmap, 0, 0, width, height);

  const mimeType = file.type === "image/png" ? "image/png" : "image/jpeg";
  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((result) => (result ? resolve(result) : reject(new Error("图片压缩失败"))), mimeType, 0.75);
  });
  const extension = mimeType === "image/png" ? "png" : "jpg";
  return new File([blob], `comment-${Date.now()}.${extension}`, { type: mimeType });
}

function loadImage(file: File) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("图片读取失败"));
    };
    image.src = url;
  });
}

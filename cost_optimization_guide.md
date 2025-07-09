# 💰 Cost Optimization Guide for Russian ABC Poster Generation

## Current Settings (Default)
- **Image Size**: `1024x1024` (only practical option for square images)
- **Image Quality**: `high` (most expensive)
- **Cost**: ~$0.08 per image

## ⚠️ Important: gpt-image-1 Size Limitations
The `gpt-image-1` model only supports these sizes:
- `1024x1024` (square - best for flashcards)
- `1024x1536` (portrait)
- `1536x1024` (landscape)
- `auto` (model decides)

**No smaller sizes available** for cost reduction through resolution.

## 🔧 Cost-Saving Options Available

### Quality Optimization (Primary Cost Savings)
```bash
# In your .env file, add:
IMAGE_QUALITY=medium    # ~40% cost reduction
# OR
IMAGE_QUALITY=low       # ~60% cost reduction
```

### Maximum Cost Savings
```bash
# Best cost savings available:
IMAGE_SIZE=1024x1024      # Required for square flashcards
IMAGE_QUALITY=medium      # ~40% cost reduction
```

## 📊 Realistic Cost Comparison Table

| Configuration | Size | Quality | Estimated Cost | Savings | Recommended Use |
|---------------|------|---------|---------------|---------|-----------------|
| **Default (Current)** | 1024x1024 | high | $0.08 | 0% | Final production |
| **Economy** | 1024x1024 | medium | $0.05 | ~40% | Testing & drafts |
| **Budget** | 1024x1024 | low | $0.03 | ~60% | Quick tests |

## 🚀 How to Apply Cost Settings

### Method 1: Environment Variables
Create/edit your `.env` file:
```bash
# Cost optimization settings
IMAGE_SIZE=1024x1024     # Keep square format
IMAGE_QUALITY=medium     # Reduce cost ~40%
```

### Method 2: Export Environment Variables (Temporary)
```bash
export IMAGE_SIZE=1024x1024
export IMAGE_QUALITY=medium
```

## 💡 Recommendations

### For Testing & Development:
```bash
IMAGE_SIZE=1024x1024
IMAGE_QUALITY=medium
```
- **Savings**: ~40% cost reduction
- **Quality**: Still very good for educational flashcards
- **Speed**: Faster generation

### For Final Production:
```bash
IMAGE_SIZE=1024x1024
IMAGE_QUALITY=high
```
- **Best Quality**: Maximum quality
- **Use**: Only for final poster generation

## 📝 Quick Test Commands

### Test with Economy Settings:
```bash
export IMAGE_SIZE=1024x1024
export IMAGE_QUALITY=medium
python src/agents/hybrid_picture_generator.py А арбуз
```

### Generate 10 Letters with Economy Settings:
```bash
export IMAGE_SIZE=1024x1024
export IMAGE_QUALITY=medium
python src/agents/coordinator.py --limit 10
```

## 🎯 Impact on Poster Quality

- **1024x1024 images** are perfect for the 400px poster cells
- **Medium quality** is excellent for educational flashcards
- **No visual quality loss** for the target poster size
- **Solid cost savings** of ~40% with no downsides

## ⚡ Immediate Cost Reduction

To start saving immediately, run:
```bash
echo 'IMAGE_SIZE=1024x1024' >> .env
echo 'IMAGE_QUALITY=medium' >> .env
```

This will reduce your image generation costs by approximately **40%** while maintaining excellent quality for your Russian alphabet poster! 
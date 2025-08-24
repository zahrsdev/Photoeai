"""
Smart Prompt Compressor Service for PhotoeAI

This service intelligently compresses long, enhanced photography briefs into dense,
powerful prompts that respect API character limits while preserving artistic essence.
"""

from typing import Optional
from loguru import logger
from app.services.ai_client import AIClient


class PromptCompressorService:
    """
    Service that compresses long photography briefs into effective image generation prompts.
    
    Uses AI to extract key visual concepts and compress them into dense, powerful paragraphs
    while maintaining the creative vision and technical specifications.
    """
    
    def __init__(self):
        """Initialize the compressor service with AI client."""
        self.ai_client = AIClient()
    
    async def compress_brief_for_generation(self, brief_text: str, max_length: int = 4000) -> str:
        """
        Compress a long photography brief into a powerful, dense prompt for image generation.
        
        Args:
            brief_text: The long, enhanced photography brief to compress
            max_length: Maximum character limit for the compressed prompt
            
        Returns:
            Compressed prompt optimized for image generation APIs
        """
        # If the brief is already within limits, return as-is
        if len(brief_text) <= max_length:
            logger.info(f"📏 Brief already within limits ({len(brief_text)} chars), no compression needed")
            return brief_text
        
        request_id = hash(brief_text) % 10000  # Simple request tracking
        
        logger.info(f"🔧 COMPRESSION: Starting smart brief compression [ID: {request_id}]", extra={
            "request_id": request_id,
            "original_length": len(brief_text),
            "target_max_length": max_length,
            "compression_needed": len(brief_text) - max_length,
            "operation": "compress_brief_for_generation"
        })
        
        try:
            compression_instruction = f"""
You are an expert AI Prompt Engineer for image generation models like DALL-E 3. Your task is to take a long, descriptive photography brief and compress it into a single, dense paragraph that captures all the essential visual elements.

**CRITICAL INSTRUCTIONS:**
1.  **Extract Key Concepts**: Identify and extract the most critical artistic and technical keywords from the brief below (e.g., "matte black jar", "dramatic yet refined studio lighting", "textured black marble surface", "Canon EOS R5", "50mm f/1.8", "creamy bokeh", "ethereal smoke", "cool, desaturated grading").
2.  **Synthesize into a Dense Paragraph**: Combine all these keywords and concepts into a single, comma-separated, highly descriptive paragraph that flows naturally while being information-dense.
3.  **Prioritize Visuals**: Focus on words that describe visual elements, lighting, composition, mood, materials, textures, and technical camera details. Omit section headers, narrative rationale, and process explanations.
4.  **Preserve Technical Details**: Keep specific camera models, lens specifications, lighting setups, and post-processing notes as these are crucial for image quality.
5.  **Maintain Creative Vision**: Ensure the emotional tone and artistic vision from the original brief is preserved in the compressed version.
6.  **Respect Character Limit**: The final output MUST be under {max_length} characters while being as comprehensive as possible.

**Long Brief to Compress:**
---
{brief_text}
---

Now, produce the single, compressed, and powerful paragraph for the image generation model. Focus on creating a flowing, natural description that reads like a professional photography prompt while being incredibly dense with visual information.
"""
            
            logger.debug(f"📝 Sending compression request to AI [ID: {request_id}]", extra={
                "request_id": request_id,
                "instruction_length": len(compression_instruction),
                "temperature": 0.6
            })
            
            response = await self.ai_client.generate_text(compression_instruction)
            compressed_prompt = response.strip()
            
            # Verify compression was successful
            if len(compressed_prompt) > max_length:
                logger.warning(f"⚠️ AI compression exceeded limit, applying hard truncation [ID: {request_id}]")
                # Apply smart truncation as fallback
                compressed_prompt = self._smart_truncate(compressed_prompt, max_length)
            
            compression_ratio = len(compressed_prompt) / len(brief_text) if brief_text else 0
            
            logger.info(f"✅ COMPRESSION: Smart compression completed [ID: {request_id}]", extra={
                "request_id": request_id,
                "original_length": len(brief_text),
                "compressed_length": len(compressed_prompt),
                "compression_ratio": round(compression_ratio, 3),
                "characters_saved": len(brief_text) - len(compressed_prompt),
                "operation": "compress_brief_for_generation",
                "status": "success"
            })
            
            return compressed_prompt
            
        except Exception as e:
            logger.error(f"💥 COMPRESSION ERROR [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "compress_brief_for_generation",
                "status": "error"
            })
            
            # Fallback: Use smart truncation of the original brief
            logger.warning(f"⚠️ AI compression failed, falling back to smart truncation [ID: {request_id}]")
            return self._smart_truncate(brief_text, max_length)
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """
        Intelligently truncate text while preserving meaning.
        
        Tries to end at natural break points like section breaks, sentences, or words.
        """
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        
        logger.debug(f"🔪 Applying smart truncation from {len(text)} to {max_length} chars")
        
        # Try to end at a section break (markdown headers or separators)
        section_break = max(
            truncated.rfind('\n## '),
            truncated.rfind('\n### '),
            truncated.rfind('\n---\n'),
            truncated.rfind('\n**')
        )
        if section_break > max_length * 0.7:  # Only if we don't lose too much content
            result = text[:section_break]
            logger.debug(f"✂️ Truncated at section break to {len(result)} characters")
            return result
        
        # Try to end at a complete sentence
        sentence_end = max(
            truncated.rfind('. '),
            truncated.rfind('.\n'),
            truncated.rfind('! '),
            truncated.rfind('? ')
        )
        if sentence_end > max_length * 0.8:  # Only if we don't lose too much content
            result = text[:sentence_end + 1]
            logger.debug(f"✂️ Truncated at sentence end to {len(result)} characters")
            return result
        
        # Fall back to word boundary
        word_boundary = truncated.rfind(' ')
        if word_boundary > 0:
            result = text[:word_boundary]
            logger.debug(f"✂️ Truncated at word boundary to {len(result)} characters")
            return result
        
        # Last resort: hard truncation
        logger.debug(f"✂️ Applied hard truncation to {max_length} characters")
        return truncated


# Create a global instance for easy import
prompt_compressor = PromptCompressorService()

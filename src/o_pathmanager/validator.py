# pathmanager/validator.py

import re
from abc import ABC, abstractmethod
from typing import Dict

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, template_name: str, tokens: Dict[str, str], tpl_conf: dict) -> None:
        """Validate tokens against template constraints."""
        pass

class TokenValidatorStrategy(ValidationStrategy):
    #__DESCRIPTOR_ALLOWED = {'temp', 'review', 'delivery', 'final', 'precomp'}
    #__REP_TOKEN_PATTERN   = re.compile(r'^[a-z0-9]+_[a-z0-9]+_[a-z0-9]+$')
    #__LAYERID_TOKEN_PATTERN = re.compile(r'^[A-Za-z]$')

    def validate(self, template_name: str, tokens: Dict[str, str], tpl_conf: dict) -> None:
        # 1) rep token
        #rep = tokens.get('rep')
        #if rep and not self.__REP_TOKEN_PATTERN.match(rep):
        #    raise ValueError(f"Invalid rep '{rep}' for template '{template_name}'")

        # 2) descriptor token
        #descriptor = tokens.get('descriptor')
        #if descriptor and descriptor not in self.__DESCRIPTOR_ALLOWED:
        #    raise ValueError(f"Invalid descriptor '{descriptor}' for template '{template_name}'")

        # 3) layerID token
        #layerID = tokens.get('layerID')
        #if layerID is not None and not self.__LAYERID_TOKEN_PATTERN.match(layerID):
        #    raise ValueError(
        #        f"Invalid layerID '{layerID}' for template '{template_name}'. Must be a single letter."
        #    )

        # 4) eye token against allowed_eyes
        allowed_eyes = tpl_conf.get('allowed_eyes', [])
        eye = tokens.get('eye')
        if allowed_eyes and eye and eye not in allowed_eyes:
            raise ValueError(f"Eye '{eye}' not allowed for template '{template_name}'")
        
        # 5) sequence vs single‐file enforcement
        #ext      = tokens.get('ext', '').lower()
        #padding  = tokens.get('padding', '')
        #seq_exts = tpl_conf.get('sequence_exts', [])

        #if seq_exts:
        #    # If it's one of the “is a sequence” extensions, padding is mandatory
        #    if ext in seq_exts and not padding:
        #        raise ValueError(
        #            f"Template '{template_name}' requires a padding token when ext='{ext}'"
        #        )
        #    # If it’s not in that list, padding must be empty
        #    if ext not in seq_exts and padding:
        #        raise ValueError(
        #            f"Template '{template_name}' should not have padding when ext='{ext}'"
        #        )

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import traitlets as tr
from traitlets import TraitError
import numpy as np
from six import string_types


VECTOR_DIRECTIONS = dict(
    X=[1, 0, 0],
    Y=[0, 1, 0],
    Z=[0, 0, 1],
    EAST=[1, 0, 0],
    WEST=[-1, 0, 0],
    NORTH=[0, 1, 0],
    SOUTH=[0, -1, 0],
    UP=[0, 0, 1],
    DOWN=[0, 0, -1],
)


class DocumentedTrait(tr.TraitType):
    """A mixin for documenting traits"""

    sphinx_extra = ''

    @property
    def sphinx_class(self):
        return ':class:`{cls} <.{cls}>`'.format(cls=self.__class__.__name__)

    def sphinx(self, name):
        if not isinstance(self, tr.TraitType):
            return ''
        return (
            ':param {name}: {doc}\n:type {name}: {cls}'.format(
                name=name,
                doc=self.help + self.sphinx_extra,
                cls=self.sphinx_class
            )
        )


class Vector(DocumentedTrait):
    """A vector trait"""

    def __init__(self, normalize=False, length=1.0, **kwargs):
        assert isinstance(normalize, bool), 'normalize must be a boolean'
        assert isinstance(length, float), 'length must be a float'
        self.normalize = normalize
        self.length = length
        super(Vector, self).__init__(**kwargs)

    def validate(self, obj, value):
        """Determine if array is valid based on shape and dtype"""
        if isinstance(value, string_types):
            if value.upper() not in VECTOR_DIRECTIONS:
                self.error(obj, value)
            value = VECTOR_DIRECTIONS[value.upper()]
        if not isinstance(value, (list, np.ndarray)):
            self.error(obj, value)
        value = np.array(value)
        if value.size != 3:
            self.error(obj, value)

        out = value.flatten().astype(float)
        if self.normalize:
            norm = (out ** 2).sum()
            if norm > 0.0:
                out = out * (1.0 / norm) * self.length
            else:
                # Cannot normalize a zero length vector
                self.error(obj, value)
        return out

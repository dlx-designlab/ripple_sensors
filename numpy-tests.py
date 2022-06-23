from nis import match
import numpy
a = numpy.array([3, 4])
b = numpy.array([ [3, 4], [2, 8], [3, 4] ])

matches = numpy.all(a==b, axis=1)

print(matches)
print(numpy.where(matches))
print((a==b))

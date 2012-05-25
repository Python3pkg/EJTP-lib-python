'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''


import thread
import encryptor

from Crypto.PublicKey import RSA as rsalib

class RSA(encryptor.Encryptor):
	def __init__(self, keystr):
		self.keystr = keystr
		self._key = None
		self.genlock = thread.allocate()
		if keystr == None:
			self.genlock.acquire()
			self.generate()
		else:
			self._key = rsalib.importKey(keystr)

	def encrypt(self, value):
		# Process in blocks
		value = str(value)
		result = []
		marker = 0
		totallen = len(value)
		while marker < totallen:
			result.append(self.key.encrypt(
				value[marker:marker+self.blocksize], "")[0])
			marker += self.blocksize
		return "".join(result)

	def decrypt(self, value):
		value = str(value)
		result = []
		marker = 0
		totallen = len(value)
		while marker < totallen:
			result.append(self.key.decrypt(value[marker:marker+128]))
			marker += 128
		return "".join(result)

	@property
	def key(self):
		with self.genlock:
			return self._key

	@property
	def blocksize(self):
		# If you try to encrypt strings longer than the block size...
		# well, enjoy your heaping helping of useless gibberish.
		# This wrapper class handles blocking and deblocking for you.
		#return self.key.size()/8-11 # May be overzealous, but better than not.
		return 128

	def generate(self, bits=1024):
		thread.start_new_thread(self._generate, (bits,))

	def _generate(self, bits):
		try:
			self._key = rsalib.generate(bits)
		finally:
			self.genlock.release()

	def proto(self):
		return ['rsa', self.key.exportKey()]

	def public(self):
		key = self.key.publickey()
		return ['rsa', key.exportKey()]
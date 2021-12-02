# For this script to work, you need
# to edit line 49 of libs\anvilparser\anvil\empty_region.py ( First line of function inside() )
# to return True because one of the checks is messed up
# https://github.com/matcool/anvil-parser/issues/27

import libs.anvilparser.anvil as anvil

def getChunkVersion(chunk):
	if chunk["DataVersion"].value < 2860:
		return 17 # 1.17-
	else:
		return 18 # 1.18+

def seventeenChecks(chunk):
	return (
		"Biomes" in chunk["Level"] # Chunk has been loaded
		and chunk["Level"]["InhabitedTime"].value > 0 # Chunk has been visisted
		)

def eighteenChecks(chunk):
	return (
		chunk["Status"].value == "full" # Minecraft thinks the chunk has been fully populated/loaded
		and chunk["InhabitedTime"].value > 0 # Chunk has been visited/loaded by a player
		)

def removeEmptyChunks(regionX,regionZ,directory):
	region = anvil.Region.from_file(directory+'r.'+str(regionX)+"."+str(regionZ)+'.mca')
	newRegion = anvil.EmptyRegion(regionX,regionZ)
	isEmpty = True
	for chunkX in range(0,32):
		for chunkZ in range(0,32):
			chunk = region.chunk_data(chunkX,chunkZ)
			if chunk:
				ver = getChunkVersion(chunk)
				if ver == 17 and seventeenChecks(chunk):
					newRegion.add_chunk(anvil.Chunk.from_region(region,chunkX,chunkZ))
					isEmpty = False
				elif ver >= 18 and eighteenChecks(chunk):
					newRegion.add_chunk(anvil.Chunk.from_region(region,chunkX,chunkZ))
					isEmpty = False
	if isEmpty:
		return None
	else:
		return newRegion

if __name__ == "__main__":
	import os
	import re
	from multiprocessing.pool import ThreadPool as Pool
	import multiprocessing

	inputDir = "./input/"
	outputDir = "./output/"

	def worker(regionCoords):
		filename = "r."+regionCoords[0]+"."+regionCoords[1]+".mca"
		region = removeEmptyChunks(regionCoords[0],regionCoords[1], inputDir)
		if region:
			print(filename+" has been cleaned! Saving..")
			region.save(outputDir+filename)
		else:
			print("Removing file '"+filename+"' as it contains nothing but empty chunks.")

	with Pool(multiprocessing.cpu_count()) as pool:
		regions = []
		for item in os.scandir(inputDir):
			if item.path.endswith(".mca") and item.is_file(): # if it's a mca file...
				regionCoords = re.findall('r\.(-?\d+)\.(-?\d+)\.mca',item.name)[0] # Extract the region coordinates from the file name
				if regionCoords:
					regions.append(regionCoords)
		pool.map(worker,regions)

	print("Done!")
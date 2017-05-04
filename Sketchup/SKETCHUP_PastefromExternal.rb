#######################################################################
# copy and paste the contents of this script into the ruby console in #
# sketchup under Windows/Ruby console                                 #
#######################################################################

require 'tmpdir'
temp = Dir.tmpdir()
file = temp + "/" + "ODVertexData.txt"

lines = Array.new
File.open(file).each { |line| lines << line }

vertstart = 0
vertcount = 0
polystart = 0
polycount = 0

count = 0
for line in lines do
    if (line.match(/^VERTICES:/))
        vertstart = count
        vertcount = (line.split(':').last).to_i
    end
    if (line.match(/^POLYGONS:/))
        polystart = count
        polycount = (line.split(':').last).to_i
    end
    count = count + 1
end

#grab the points from the File and put them in an array
#I multiply the scale by 100 here from cm to meters.
points = Array.new
for i in vertstart+1..vertstart + vertcount do
    inter = lines[i].strip.split(" ")
    points.push([inter[0].to_f*100, inter[2].to_f*100, inter[1].to_f*-100])
end

model = Sketchup.active_model
entities = model.active_entities

#grab the polygon description and add the faces
for i in polystart+1..polystart + polycount do
    pts = Array.new
    line = lines[i].split(";;").first.split(",")
    for pt in line do
        pts.push(pt.to_i)
    end
    entities.add_face(points[pts[0]], points[pts[1]], points[pts[2]], points[pts[3]])
end

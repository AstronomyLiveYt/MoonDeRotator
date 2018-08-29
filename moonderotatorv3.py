import ephem
import cv2
import sys
import math
import imutils

def equatorial_to_horizon(dec, H, lat):
    alt = math.asin(math.sin(dec)*math.sin(lat)+math.cos(dec)*math.cos(lat)*math.cos(H))
    az = math.acos((math.sin(dec)-math.sin(lat)*math.sin(alt))/(math.cos(lat)*math.cos(alt)))
    if math.sin(H)>0:
        az = (360 - (az * 180/math.pi))*(math.pi/180)
    return(alt, az)

def position_angle(alpha1, sigma1, alpha2, sigma2):
    positionangle = math.atan2((math.cos(sigma2)*math.sin(alpha2-alpha1)),
    (math.cos(sigma1)*math.sin(sigma2)-math.sin(sigma1)*math.cos(sigma2)*math.cos(alpha2-alpha1)))
    return(positionangle)

observer = ephem.Observer()
observer.lat = sys.argv[1]
observer.lon = sys.argv[2]
observer.elevation = float(sys.argv[3])
observer.date = str(sys.argv[4]+" "+sys.argv[5])
moon = ephem.Moon(observer)
sun = ephem.Sun(observer)
ramoon = moon.ra
decmoon = moon.dec
siderealtime = observer.sidereal_time()
hourangle = (siderealtime - moon.ra)
altmoon, azmoon = equatorial_to_horizon(decmoon, hourangle, observer.lat)
rasun = sun.ra
decsun = sun.dec
print("The moon's altitude was: %.2f" % (altmoon * 180/math.pi), "degrees.  The moon's azimuth was: %.2f" % (azmoon * 180/math.pi), "degrees.")
k = 15.04106858 * math.cos(observer.lat)
instantrate = k * (math.cos(azmoon)/math.cos(altmoon))
print("The instantaneous rate of field rotation at this altitude and azimuth was: %.2f" % instantrate, "degrees/hr according to the RASC Calgary formula.")
posangle = position_angle(moon.ra, moon.dec, sun.ra, sun.dec)
posangledegrees = posangle * 180/math.pi
print("The position-angle of the moon's bright limb in the equatorial coordinate system was: %.2f" % posangledegrees, "degrees.")
moonradius = ((moon.size/3600)/2)*(math.pi/180)
decmoonnorth = decmoon + moonradius
altnorth, aznorth = equatorial_to_horizon(decmoonnorth, hourangle, observer.lat)
fieldrotation = position_angle(azmoon, altmoon, aznorth, altnorth)
print("The field rotation of the moon in the altitude/azimuth coordinate system was: %.2f" % (fieldrotation * 180/math.pi), "degrees.")
moonorient = (posangle+(math.radians(90))) - fieldrotation
if moonorient > math.radians(90):
    moonorient = moonorient - math.radians(180)
print("Rotate the moon by %.2f" % (moonorient * 180/math.pi), "degrees to return it to a vertical orientation.")
if len(sys.argv) > 6:
    image = cv2.imread(sys.argv[6])
    rotated = imutils.rotate_bound(image, (1*(moonorient* 180/math.pi)))
    imagename = sys.argv[6].split('.')
    newimagename = imagename[0] + "_Derotated." + imagename[1]
    cv2.imwrite(newimagename, rotated)
    cv2.imshow("De-rotated", rotated)
    cv2.imshow("Original", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

library(raster)

# incarcam rasterul in R; previzualizam datele
tg <- brick('~/Desktop/ugal/R/ecad_2.nc')
plot(tg) # ploteaza harti pentru primele 10 strate
plot(tg[[1]]) # ploteaza temp. pentru prima zi (01-01-1951)
hist(tg[[1:4]]) # histograme pentru primele patru rastere
boxplot(tg[[1:4]]) # boxplot pt primele 4 rastere

# informatii generale
tg # vezi info despre rezolutie, extent, proiectie etc.
nlayers(tg) # arata numarul de zile

# extrage atributul 'Date' pentru a calcula valori lunare, anuale, etc
date <- names(tg) # extrage campul 'date' intr-un vector separat
date <- substr(date, 2, length(date)) # elimina X din fata campului data
str(date) # vezi structura vectorului; este caracter si trebuie convertit in format 'Date' readeble by computer
date <- as.Date(date, format('%Y.%m.%d')) # converteste din format caracter (string) in Date
summary(date) # vezi informatii generale despre date

# atribuie atributul Date rasterului de date
tg <- setZ(tg, date)

# calculeaza medii lunare
lunare <- zApply(tg, format(date, "%m"), FUN = mean) # agrega din valori zilnice in lunare
plot(lunare)


# extrage date lunare pt cateva localitati (Galati, Iasi, Bucuresti, Cluj)
library(rgdal)

# creaza metadata pt fiecare locatie 
galati <- data.frame(lat = 45.423333, lon = 28.0425, localitate = 'Galati')
iasi <- data.frame(lat = 47.162222, lon =  27.588889, localitate = 'Iasi')
bucuresti <- data.frame(lat = 44.4325, lon =  26.103889, localitate = 'Bucuresti')
cluj <- data.frame(lat = 46.766667, lon =  23.583333, localitate = 'Cluj')

locatii <- rbind(galati, iasi, bucuresti, cluj) # uneste toate locatiile intr-un singur tabel
locatii <- SpatialPointsDataFrame(locatii, coords = locatii[, c(2, 1)])
crs(locatii)<- '+proj=longlat +datum=WGS84 +no_defs'

extractie <- extract(lunare, locatii, df = T)
extractie$locatie <- locatii$localitate
extractie$ID <- NULL
names(extractie)[1:12] <- month.abb

# ploteaza grafice
library(reshape2)
library(ggplot2)

extractie_melt <- melt(extractie, id = c('locatie')) # converteste din wide in long format
head(extractie_melt)

ggplot(extractie_melt, aes(x = variable, y = value)) +
  geom_bar(stat = 'identity') +
  facet_wrap(~ locatie) +
  theme_classic() +
  theme(text = element_text(size = 16)) +
  ylab('grade Celsius [°C]') + xlab('luna') +
  ggtitle('Temperatura medie lunara multianuala a aerului', subtitle = 'din ECA&d v25. Perioada:2010-2021')

# ploteaza harta cu temperatura medie lunara
cordinates <- coordinates(lunare)
lunare_st <- as.data.frame(lunare)
lunare_st <- cbind(lunare_st, cordinates)

lunare_st <- na.omit(lunare_st)
lunare_st <- melt(lunare_st, id = c('x', 'y'))
lunare_st$discrete <- cut(lunare_st$value, breaks  = seq(-25, 40, 5), labels = seq(-25, 35, 5))

# creaza o paleta de culori (predefinita - vezi https://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3)
cols <- rev(RColorBrewer::brewer.pal(11, 'RdYlBu'))
cols <- colorRampPalette(cols)(14) 

ggplot() +
  geom_tile(data = lunare_st , aes(x = x, y = y, fill = discrete)) +
  facet_wrap(~ variable, ncol = 4) +
  theme_bw() +
  labs(x = NULL, y = NULL) +
  scale_fill_manual(values = cols, name = NULL, na.value="transparent") +
  theme(legend.position = 'bottom', legend.direction = 'horizontal', legend.box = "horizontal",
        legend.key.width = unit(3,"line"), legend.key.height = unit(2, 'line'), legend.text=element_text(size=20),
        legend.key = element_rect(color="black"), # add black color around legend
        text = element_text(size = 20), 
        panel.background = element_rect(fill = 'white'),
        panel.spacing = unit(1, 'mm'),
        strip.background=element_rect(colour="black", 
                                      fill="white")) +
  guides(fill = guide_legend(hjust = 0.2, label.position = "bottom", nrow = 1, byrow = T, title = '°C'))

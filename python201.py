# # Breakdown and recreate Risk Capital calculation script

# define start date and end date
startD = "09/11/2018"
endD = "09/11/2018"

#1. Collect input files (cons, input). Define newly created file and path. 

#2. read pa2 file

#3. read 3 constant files

#4. calculate new stretched scan range, intermonth, intercomm

#5. write risk capital pa2 file
# new pa2 file wouldn't have new risk array calculated, has to be recalculated using whatif file

#6. write whatif file 

#7. read position file

#8. calculate and write position file with sum positions

#9. calculate and get report for:
#9.1. margin

#9.2. risk capital

#10. calculate delta adjusted net exposure for options

#11. read cons house file

#12. read pbreq margin and pbreq risk capital files

#13. use criteria rule to generate risk capital for each participant

#14. write final excel file
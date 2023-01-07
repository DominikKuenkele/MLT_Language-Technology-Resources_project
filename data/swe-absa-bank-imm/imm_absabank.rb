PATH = "annotation" #where the original annotation is stored
PATH2 = "source" #where the original sources are stored
PATH3 = "documents" #where to copy the sources

STDERR.puts "Usage: Download the original Absabank, unzip the two archives and combine the files. Run ruby imm_absabank level, where level is either D(ocument) or P(aragraph)"
level = ARGV[0] #D or P

#flags that enable additional analysis. Not fully documented, do not affect the conversion itself
annotator_stats = false #output statistics per annotator?
sd_analysis = false #extract the texts annotated by a given set of annotators 
list_combinations = false #list combinations of users and the number of texts annotated by every user in the combination

if list_combinations
    combinations = Hash.new{0}
    small_combinations = []
    smallcomb_threshold = 2
    comb_file = File.open("comb#{smallcomb_threshold}.tsv","w:utf-8")
end


#see readme.txt

output = File.open("#{level}_annotation.tsv","w:utf-8")
#output_users = File.open("#{level}_users.tsv","w:utf-8")
if level == "P" 
    output.puts "doc\tpar\tn_opinions\tmin\tmax\taverage\tsd\tsimplified\t0\t1\t3\t4\t6\t7\t8\t9\t10\t11\tsign_conflict?\ttitle?\ttext" 
    #output_users.puts "doc\tpar\tuser\tsentiment" 
else
    output.puts "doc\tn_opinions\tmin\tmax\taverage\tsd\tsimplified\t0\t1\t3\t4\t6\t7\t8\t9\t10\t11\tsign_conflict?" 
    #output_users.puts "doc\tuser\tsentiment" 
end

if sd_analysis or list_combinations
    def comb_in_comb(smallcomb, largecomb)
        sc = smallcomb.split(";")
        lc = largecomb.split(";")
        flag = true
        sc.each do |user|
            if !lc.include?(user)
                flag = false
                break
            end
        end
       return flag
    end
    if sd_analysis
        source = "7;8;11" # #7;8;11
        sd_file = File.open("sd_source#{source}.tsv","w:utf-8")
        sd_file.puts "doc\tpar\taverage\tsd\tsimplified\t#{source.split(";").join("\t")}\tsign_conflict?\ttext" 
    end
end
    


#copy the source text. Do it for all sources, even those that are not D- or P-level annotated
def get_source_text(filename)
    tokens = 0
    sfile = File.open("#{PATH2}\\#{filename}", "r:utf-8")
    ofile = File.open("#{PATH3}\\#{filename}.txt", "w:utf-8")
    sfile.each_line do |line|
        line1 = line.strip
        if !["","#D IMM.","#T IMM.", "#P IMM."].include?(line1)
            ofile.puts line1
            tokens += line1.count(" ") + 1
        end
    end
    #STDERR.puts tokens
    return tokens
    
end

def voting(array)
    #5/1: 2 voices for pos/neg, 4/2: 1 voice, 3: 1 voice for neut. If tie neut vs. marked, choose marked. If tie pos vs. neg, choose neut.
    pos = array.count(5)*2 + array.count(4)
    neg = array.count(1)*2 + array.count(2)
    if pos > neg
        vote = 1
    elsif neg > pos 
        vote = -1
    else
        vote = 0
    end
    return vote
end


#store the paragraph text in hash, include  annotated paragraphs in the spreadsheet later
def get_source_pars(filename, output)
    tokenhash = Hash.new(0)
    sfile = File.open("#{PATH2}\\#{filename}", "r:utf-8")
    p = 0
    flag = 0
    ofile = ""
    parhash = Hash.new{|hash, key| hash[key] = Array.new}
    titlehash = Hash.new("")
    
    sfile.each_line do |line|
        line1 = line.strip
        if line1 == "#P IMM." or line1 == "#T IMM."
            p += 1
            if line1 == "#T IMM."
                titlehash[p] = "title"
            end
            if output == "file"
                ofile = File.open("#{PATH4}\\#{filename}_#{p}.txt", "w:utf-8")
            end
            flag = 3
        end
        if flag > 1
            if line1 !="" 
                if line1 != "#P IMM." and line1 != "#T IMM."
                    if output == "file"
                        ofile.puts line1
                    else
                        parhash[p] << line1.strip.gsub("\t","")
                    end
                    tokenhash[p] += line1.count(" ") + 1
                end
            else
                flag -= 1
            end
        elsif flag == 1 and output == "file"
            ofile.close
        end
    end
    
    #STDERR.puts tokenhash
    return parhash, titlehash, tokenhash
    
end

#calculate mean and sd
def stats(input, type)
    if type == "hash"
        sent_array = input.values
    elsif type == "array"
        sent_array = input
    end
    sent_sum = 0.0
    sent_array.each do |sent|
        sent_sum += sent
    end
    mean = sent_sum/sent_array.length
    
    sumsq = 0.0
    sent_array.each do |sent|
        sumsq += (mean - sent)*(mean - sent)
    end
    sd = Math.sqrt(sumsq/sent_array.length)
    return mean, sd
end

ntokens = 0

dirlist = Dir.children(PATH) #all folders in the annotation folder

output_storage = Hash.new{|hash, key| hash[key] = Array.new}
users_total = Hash.new{|hash, key| hash[key] = Array.new}

dirlist.each do |dir|
    if dir != "z01240_flashback-56154591" #excluding the document which contains ironic paragraphs (see readme)
        filelist = Dir.children("#{PATH}\\#{dir}") #all annotator files
        sentiments = {}
        users = []
        #sent_hash = Hash.new{|hash, key| hash[key] = Array.new} #for storing sentiment values
        sent_hash = Hash.new{|hash, key| hash[key] = Hash.new{""}} #for storing sentiment values
	    
        if level == "D"
            tokens = get_source_text(dir)
        elsif level == "P"
            parhash, titlehash, tokenhash = get_source_pars(dir, "nofile") #resp.: the paragraph itself, whether it's the title, how many tokens
        end
        
        par = 0
        countingflag = Hash.new{true} #to keep track of whether this paragraph has already been considered when counting the total number of tokens
	    
        filelist.each do |file|
            par = 0
            if file[0..-5] != "jacobo" #ignore Jacobo according to his recommendation 
                if file[0..-5] == "lars" #recode Lars as user 0
                    user = 0
                else
                    user = file.split(".")[0][4..-1].to_i
                end
                
                f = File.open("#{PATH}\\#{dir}\\#{file}","r:utf-8")
                handle = false #whether we are at the P or D level
                f.each_line.with_index do |line, lineindex|
                    line1 = line.strip
                    
                    if line1.include?("#Text=##{level} IMM.") or (level == "P" and line1.include?("#Text=#T IMM."))
                        handle = true 
                    end
                    if handle
                        line2 = line1.split("\t")
                        if line2[2] == "IMM" #if we found the necessary line
                            ok_length = true
                            
                            #testing whether any other columns than 6 or 7 can contain sentiment annotation
                            #line2.each.with_index do |col, colindex|
                            #    if [1,2,3,4,5].include?(col[0].to_i) and ![0,1,2,6,7].include?(colindex)
                            #        STDOUT.puts "#{dir} #{user} #{lineindex}"
                            #    end
                            #end
	    
                            if line2.length > 7
                                sent_index = 7
                                irony_index = 6
                            elsif line2.length == 7
                                sent_index = 6
                                irony_index = 5
                            else
                                ok_length = false #I am not entirely sure, but it seems the shorter lines always lack the annotation
                            end
	    
                            if ok_length
                                if level == "P"
                                    par += 1 #numbering the paragraphs to interpret the hashes correctly
                                end
                                
                                
                                users << user
                                sentiments[user] = line2[sent_index][0]
                                
	    
                                if line2[irony_index].include?("false")
                                    irony = "false"
                                elsif line2[irony_index].include?("true")
                                    irony = "true"
                                end
                                
                                #if level == "P"
                                #    output_users.puts "#{dir}\t#{par}\t#{user}\t#{sentiments[user]}" 
                                #else
                                #    output_users.puts "#{dir}\t#{user}\t#{sentiments[user]}" 
                                #end
	    
                                if sentiments[user] != "_" #if annotation is not empty
                                    #sent_hash[par] << sentiments[user].to_i
                                    sent_hash[par][user] = sentiments[user].to_i
                                    users_total[user] << sentiments[user].to_i
                                    if countingflag[par] #if this paragraph/documents has not yet been counted when counting tokens
                                        #STDERR.puts "#{dir}, #{user}, #{par}, #{sentiments[user].to_i}"
                                        if level == "P"
                                            ntokens += tokenhash[par]
                                        else
                                            ntokens += tokens
                                        end
                                    end
                                    countingflag[par] = false #do not count it anymore for other users
                                end
                                
                            end
                            if level == "D" #At D level, we do not have to look for anything else. At P level, we continue until the end
                                break
                            end
                        end
                    end
                end
                f.close
            end
        end
        
        
        sent_hash.each_pair do |par, user_hash| 
            sent_array = user_hash.values
            mean, sd = stats(sent_array, "array")
            
            if sent_array.length > 0
                # if a paragraph consists of several lines, merge these lines together (there are no cases with >2 lines)
                userstring = ""
                for i in [0,1,3,4,6,7,8,9,10,11]
                    userstring << "#{user_hash[i]}\t"
                end
	    
                
                userstring = userstring[0..-2]
                #vote = voting(sent_array)
                if mean < 3
                    vote = -1
                elsif mean > 3
                    vote = 1
                else
                    vote = 0
                end
                
                
                if (sent_array.include?(1) or sent_array.include?(2)) and (sent_array.include?(4) or sent_array.include?(4))
                    sign_disagreement = "true"
                end
	    
                if sd_analysis or list_combinations
                    combination = []
                    for j in [1,3,6,7,8,9,10,11]
                        if [1,2,3,4,5].include?(user_hash[j])
                            combination << j
                        end
                    end
                
                  if sd_analysis
                      if combination == source or comb_in_comb(source,combination.join(";"))
                          userstring2 = ""
                          isource = []
                          source.split(";").each do |u|
                              isource << u.to_i
                          end
                          for i in isource
                              userstring2 << "#{user_hash[i]}\t"
                          end
                          userstring2 = userstring2[0..-2]
                          sd_file.puts "#{dir}\t#{par}\t#{mean}\t#{sd}\t#{vote}\t#{userstring2}\t#{sign_disagreement}\t#{parhash[par][0]}"
                      end
                  end
	    
                    if list_combinations
                        combinations[combination.join(";")] += 1
                        if combination.length == smallcomb_threshold
                            small_combinations << combination.join(";")
                        end
                    end
                end
	    
                if level == "P"
                    if parhash[par].length > 1
                        parhash[par][0] = "#{parhash[par][0].strip} #{parhash[par][1].strip}"
                    end
                    output_storage[dir] << "#{dir}\t#{par}\t#{sent_array.length}\t#{sent_array.min}\t#{sent_array.max}\t#{mean}\t#{sd}\t#{vote}\t#{userstring}\t#{sign_disagreement}\t#{titlehash[par]}\t#{parhash[par][0]}"
                    #output.puts "#{dir}\t#{par}\t#{sent_array.length}\t#{sent_array.min}\t#{sent_array.max}\t#{mean}\t#{sd}\t#{vote}\t#{userstring}\t#{sign_disagreement}\t#{titlehash[par]}\t#{parhash[par][0]}"
                else
                    output_storage[dir] << "#{dir}\t#{sent_array.length}\t#{sent_array.min}\t#{sent_array.max}\t#{mean}\t#{sd}\t#{vote}\t#{userstring}\t#{sign_disagreement}"
                    #output.puts "#{dir}\t#{sent_array.length}\t#{sent_array.min}\t#{sent_array.max}\t#{mean}\t#{sd}\t#{vote}\t#{userstring}\t#{sign_disagreement}"
                end
            end
        end
    end #if dirlist != ironic doc 
end
output_storage.keys.shuffle.each do |dir|
    output.puts output_storage[dir]
end



STDERR.puts "#{level} level; #{ntokens} tokens"

if annotator_stats


    output2 = File.open("#{level}_annotators.tsv","w:utf-8")

    

    output2.puts "measure\t0\t1\t3\t4\t6\t7\t8\t9\t10\t11"
    nstring = "n"
    meanstring = "mean"
    sdstring = "sd"
    
    for i in [0,1,3,4,6,7,8,9,10,11] do 
        array = users_total[i]
        mean, sd = stats(array, "array")
        n = array.length
        nstring << "\t#{n}"
        meanstring << "\t#{mean}"
        sdstring << "\t#{sd}"
    end
    #end
    
    output2.puts nstring
    output2.puts meanstring
    output2.puts sdstring

end

if list_combinations

    small_combinations.uniq!
    combinations2 = Hash.new{0}
    combinations.each_pair do |comb, freq|
        #STDOUT.puts "#{comb}\t#{freq}\t#{comb.count(";")+1}"
        if comb.count(";") + 1 > smallcomb_threshold
            small_combinations.each do |smallcomb|
                if comb_in_comb(smallcomb,comb)
                    #STDERR.puts smallcomb, comb
                    combinations2[smallcomb] += combinations[comb]
                end
            end
        end
    end
    
    combinations2.each_pair do |comb, freq|
        freq += combinations[comb] #above, we counted only occurrences within larger combinations
        comb_file.puts "#{comb}\t#{freq}"
    end
end
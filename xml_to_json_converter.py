import json
import xmltodict
import os
from datetime import datetime

class BloombergXMLConverter:
    def __init__(self):
        self.xml_dir = "."  # Directory containing XML files
        self.json_dir = "./json_output"  # Directory for JSON output
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)

    def convert_file(self, xml_file):
        """Convert single XML file to JSON"""
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Convert XML to dict
            data_dict = xmltodict.parse(xml_content)
            
            # Create JSON filename
            base_name = os.path.splitext(os.path.basename(xml_file))[0]
            json_file = os.path.join(self.json_dir, f"{base_name}.json")
            
            # Save as JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
                
            print(f"Converted {xml_file} to {json_file}")
            return True
            
        except Exception as e:
            print(f"Error converting {xml_file}: {e}")
            return False

    def convert_all(self):
        """Convert all XML files in directory"""
        xml_files = [f for f in os.listdir(self.xml_dir) 
                    if f.endswith('.xml') and 
                    (f.startswith('twitter_feed_') or f.startswith('sentiment_'))]
        
        for xml_file in xml_files:
            self.convert_file(os.path.join(self.xml_dir, xml_file))

    def watch_and_convert(self):
        """Watch for new XML files and convert them"""
        processed_files = set()
        
        try:
            while True:
                xml_files = set([f for f in os.listdir(self.xml_dir) 
                               if f.endswith('.xml') and 
                               (f.startswith('twitter_feed_') or f.startswith('sentiment_'))])
                
                new_files = xml_files - processed_files
                
                for xml_file in new_files:
                    if self.convert_file(os.path.join(self.xml_dir, xml_file)):
                        processed_files.add(xml_file)
                
                time.sleep(1)  # Check for new files every second
                
        except KeyboardInterrupt:
            print("Stopping converter...")

def main():
    converter = BloombergXMLConverter()
    print("Starting XML to JSON converter...")
    print("Press Ctrl+C to stop")
    converter.watch_and_convert()

if __name__ == "__main__":
    main() 
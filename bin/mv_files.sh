#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== File Transfer with Progress ===${NC}"
echo ""

# Prompt for paths
read -e -p "Enter source directory path: " SOURCE_PATH
read -e -p "Enter destination directory path: " DEST_PATH

# Validate paths
if [ ! -d "$SOURCE_PATH" ]; then
    echo "Error: Source directory does not exist: $SOURCE_PATH"
    exit 1
fi

if [ ! -d "$DEST_PATH" ]; then
    echo "Error: Destination directory does not exist: $DEST_PATH"
    exit 1
fi

# Calculate total size
echo ""
echo "Calculating total size..."
TOTAL_SIZE=$(du -sb "$SOURCE_PATH" | awk '{print $1}')
TOTAL_SIZE_HUMAN=$(du -sh "$SOURCE_PATH" | awk '{print $1}')
FILE_COUNT=$(find "$SOURCE_PATH" -type f | wc -l)

echo -e "${GREEN}Source: $SOURCE_PATH${NC}"
echo -e "${GREEN}Size: $TOTAL_SIZE_HUMAN ($FILE_COUNT files)${NC}"
echo -e "${GREEN}Destination: $DEST_PATH${NC}"
echo ""

# Choose method
echo "Choose transfer method:"
echo ""
echo "1. rsync (RECOMMENDED - resumable, fastest for local)"
echo "   - Can resume if interrupted"
echo "   - Shows detailed progress"
echo "   - Optimized for local transfers"
echo ""
echo "2. tar + pv (FASTEST - raw speed)"
echo "   - Maximum speed possible"
echo "   - Good for many small files"
echo "   - Not resumable"
echo ""
echo "3. cp + watch du (SIMPLEST - standard tools)"
echo "   - Uses basic cp command"
echo "   - Monitor with separate watch command"
echo "   - Not resumable"
echo ""
read -p "Select method [1]: " METHOD
METHOD=${METHOD:-1}

case $METHOD in
    1)
        echo ""
        echo -e "${YELLOW}Using rsync with optimized flags for local transfer...${NC}"
        echo ""
        
        # Check if running in background
        read -p "Run in background? (y/n) [n]: " BG
        
        if [[ "$BG" =~ ^[Yy]$ ]]; then
            LOG_FILE="/tmp/rsync_transfer_$(date +%Y%m%d_%H%M%S).log"
            echo "Starting transfer in background..."
            echo "Log file: $LOG_FILE"
            echo ""
            
            nohup rsync -ah \
                --whole-file \
                --inplace \
                --no-compress \
                --info=progress2 \
                "$SOURCE_PATH/" "$DEST_PATH/" > "$LOG_FILE" 2>&1 &
            
            RSYNC_PID=$!
            disown $RSYNC_PID
            
            echo -e "${GREEN}✓ Transfer started (PID: $RSYNC_PID)${NC}"
            echo ""
            echo "Monitor with:"
            echo "  tail -f $LOG_FILE"
            echo ""
            echo "Check I/O:"
            echo "  iostat -xh 2"
        else
            echo "Starting transfer (Ctrl+C to cancel)..."
            echo ""
            rsync -ah \
                --whole-file \
                --inplace \
                --no-compress \
                --info=progress2 \
                "$SOURCE_PATH/" "$DEST_PATH/"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}Using tar + pv for maximum speed...${NC}"
        echo ""
        
        # Check if pv is installed
        if ! command -v pv &> /dev/null; then
            echo "Installing pv (pipe viewer)..."
            sudo apt-get update && sudo apt-get install -y pv
        fi
        
        echo "Starting transfer..."
        echo ""
        
        cd "$SOURCE_PATH" && \
        tar cf - . | pv -s "$TOTAL_SIZE" | tar xf - -C "$DEST_PATH"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ Transfer completed successfully${NC}"
        fi
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}Using cp with monitoring...${NC}"
        echo ""
        
        LOG_FILE="/tmp/cp_transfer_$(date +%Y%m%d_%H%M%S).log"
        
        echo "Starting transfer in background..."
        echo ""
        
        # Start cp in background
        (cp -r "$SOURCE_PATH"/* "$DEST_PATH/" 2>&1 && echo "COMPLETE" || echo "FAILED") > "$LOG_FILE" &
        CP_PID=$!
        
        echo -e "${GREEN}✓ Transfer started (PID: $CP_PID)${NC}"
        echo ""
        echo "Monitoring progress (press Ctrl+C to stop watching, transfer continues)..."
        echo ""
        
        # Monitor progress
        while kill -0 $CP_PID 2>/dev/null; do
            CURRENT_SIZE=$(du -sb "$DEST_PATH" 2>/dev/null | awk '{print $1}')
            CURRENT_HUMAN=$(du -sh "$DEST_PATH" 2>/dev/null | awk '{print $1}')
            
            if [ -n "$CURRENT_SIZE" ] && [ "$CURRENT_SIZE" -gt 0 ]; then
                PERCENT=$((CURRENT_SIZE * 100 / TOTAL_SIZE))
                SPEED=$(iostat -x 1 2 | grep -E "sda|sdb|sdc" | tail -1 | awk '{print $6}')
                
                echo -ne "\rProgress: $CURRENT_HUMAN / $TOTAL_SIZE_HUMAN ($PERCENT%) "
            fi
            
            sleep 2
        done
        
        echo ""
        echo ""
        
        if grep -q "COMPLETE" "$LOG_FILE"; then
            echo -e "${GREEN}✓ Transfer completed successfully${NC}"
        else
            echo "Transfer finished with errors. Check log: $LOG_FILE"
        fi
        ;;
        
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "Monitor disk I/O during transfer:"
echo "  iostat -xh 2 | grep -E 'Device|sda|sdb|sdc'"
echo ""
